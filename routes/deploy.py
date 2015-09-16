import urllib2
import yaml

try:
    import simplejson
except Exception as e:
    import json as simplejson

import traceback
import flask
from ship.logger import ShipLogger
from ship.project import ProjectBuilder
from ship.validator import *
from ship.errors import SVNException, ProjectIdNotFoundException
from commons.apps_configuration import AppsConfiguration
from commons.apps_properties import AppsProperties

apps_conf = AppsConfiguration()
apps_conf.save_todisk()

def get_deploy_config():
    f = open("config.yml")
    data = yaml.safe_load(f)
    f.close()
    return data.get('deploy')

config = get_deploy_config();
workdir = config.get("workdir")
svnurl = config.get("svnurl")
version = "trunk"
etcd_environment_url = config.get("etcd_environment_url")

deploy_app = flask.Blueprint("deploy_app", __name__, template_folder="../templates")

def get_app_acronyms(apps_conf):
    apps = [ app.upper() for app in apps_conf.get().keys() ]
    apps.sort()
    return apps


@deploy_app.route("/deploy", methods=["GET"])
def index():
    apps = get_app_acronyms(apps_conf)
    return flask.render_template("deploy.html", apps=apps)


def create_app_properties_file(app):
    app_properties = AppsProperties(app)
    app_properties.save_todisk()

@deploy_app.route("/deploy", methods=["POST"])
def deploy():
    project_name = flask.request.form["app"].lower()
    create_app_properties_file(project_name)

    try:
        flask.current_app.logger.info("Initializing project construction")

        rules = [ ConfigFileValidationRule, ConsoleLogValidationRule,
                  PomXMLValidationRule, CompiledPackageExistsValidationRule ]

        try:
            project = ProjectBuilder(workdir, project_name, "/etc/uji/%s/app.properties" % project_name) \
                .with_subversion(svnurl % (project_name.upper(), project_name), version) \
                .with_maven() \
                .with_tomcat( { "start_tomcat_after_deploy" : True }) \
                .with_validation_rules(rules) \
                .build() \
                .deploy()
        except SystemExit as e:
            flask.current_app.logger.error(traceback.format_exc())
            return "faillll"

        flask.current_app.logger.info("Finished succesfully!!")
    except SVNException as e:
        flask.current_app.logger.error("Invalid or unauthorized SVN repository "" + PROJECT_NAME + """)
        return "fail :("

    except ProjectIdNotFoundException as e:
        flask.current_app.logger.error("ProjectID not found in Tomcat")
        return "fail :("

    except Exception as e:
        flask.current_app.logger.error(traceback.format_exc())
        return "fail :("

    return  "ole :)"
