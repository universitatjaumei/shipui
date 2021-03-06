import urllib2

try:
    import simplejson
except Exception as e:
    import json as simplejson

import traceback
import flask
from ship.project import ProjectBuilder
from ship.subversion import Subversion
from ship.validator import *
from ship.errors import SVNException, ProjectIdNotFoundException
from commons.apps_configuration import AppsConfiguration
from commons.apps_properties import AppsProperties
from commons.config import Config
from flask import jsonify

config = Config()
deploy_config = config.get('deploy')
apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
apps_conf.save_todisk()

deploy_app = flask.Blueprint("deploy_app", __name__, template_folder="../templates")

def get_app_acronyms(apps_conf):
    return apps_conf.get_applications()

@deploy_app.route("/", methods=["GET"])
def index():
    apps = get_app_acronyms(apps_conf)
    return flask.render_template("deploy.html", section="deploy", apps=apps, user=flask.g.user)


def create_app_properties_file(app):
    app_properties = AppsProperties(app)
    app_properties.save_todisk()

@deploy_app.route("/versions", methods=["GET"])
def get_versions():
    project_name = flask.request.args["app"].lower()
    path = flask.request.args["path"].lower()
    versions = []

    if project_name and path:
        conf = apps_conf.get().get(project_name.lower())
        svnurl = deploy_config.get("svnurl")
        svn_web_repository = svnurl % (path.upper(), conf.get("project"))
        repo = Subversion(svn_web_repository, "/tmp", project_name)
        versions = repo.get_tags()

    return flask.jsonify({ "versions": versions })

@deploy_app.route("/", methods=["POST"])
def deploy():
    project_name = flask.request.json["app"].lower()
    path = flask.request.json["path"].lower()
    version = flask.request.json["version"].lower()

    logger = logging.getLogger('werkzeug')
    create_app_properties_file(project_name)
    logger = logging.getLogger("werkzeug")

    try:
        logger.info("Initializing project construction")

        rules = [ ConfigFileValidationRule,
                  PomXMLValidationRule, CompiledPackageExistsValidationRule ]

        conf = apps_conf.get().get(project_name.lower())
        workdir = deploy_config.get("workdir")
        svnurl = deploy_config.get("svnurl")
        svn_web_repository = svnurl % (path.upper(), conf.get("project"))

        try:
            project = ProjectBuilder(workdir, project_name, "/etc/uji/%s/app.properties" % project_name) \
                .with_subversion(svn_web_repository, version) \
                .with_maven() \
                .with_tomcat( { "start_tomcat_after_deploy" : True }) \
                .with_validation_rules(rules) \
                .build() \
                .deploy()
        except SystemExit as e:
            message = traceback.format_exc()
            logger.error(message)
            return jsonify(result={"message": message}), 500

        logger.info("Finished succesfully!!")
    except SVNException as e:
        message = "Invalid or unauthorized SVN repository " + project_name
        logger.error(message)
        return jsonify(result={"message": message}), 500

    except ProjectIdNotFoundException as e:
        message = "ProjectID not found in Tomcat"
        logger.error(message)
        return jsonify(result={"message": message}), 500

    except Exception as e:
        message = traceback.format_exc()
        logger.error(message)
        return jsonify(result={"message": message}), 500

    return jsonify(result={"status": 200})
