import urllib2

try:
    import simplejson
except Exception as e:
    import json as simplejson

import traceback
import flask
from ship.project import ProjectBuilder
from ship.validator import *
from ship.errors import SVNException, ProjectIdNotFoundException
from commons.apps_configuration import AppsConfiguration
from commons.apps_properties import AppsProperties
from commons.ship_configuration import ShipUIConfig
import flask_lsm_auth

shipui_conf = ShipUIConfig()
apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
apps_conf.save_todisk()

deploy_app = flask.Blueprint("deploy_app", __name__, template_folder="../templates")

def get_app_acronyms(apps_conf):
    apps = [ app.upper() for app in apps_conf.get().keys() ]
    apps.sort()
    return apps


@deploy_app.route("/deploy", methods=["GET"])
def index():
    apps = get_app_acronyms(apps_conf)
    lsm = flask_lsm_auth.LSM()

    return flask.render_template("deploy.html", section="deploy", apps=apps, user=lsm.get_login())


def create_app_properties_file(app):
    app_properties = AppsProperties(app)
    app_properties.save_todisk()

@deploy_app.route("/deploy", methods=["POST"])
def deploy():
    project_name = flask.request.json["app"].lower()
    create_app_properties_file(project_name)
    logger = logging.getLogger("werkzeug")

    try:
        logger.info("Initializing project construction")

        rules = [ ConfigFileValidationRule, ConsoleLogValidationRule,
                  PomXMLValidationRule, CompiledPackageExistsValidationRule ]

        conf = apps_conf.get().get(project_name.lower())
        workdir = shipui_conf.get("workdir")
        svnurl = shipui_conf.get("svnurl")
        version = shipui_conf.get("version")
        svn_web_repository = svnurl % (project_name.upper(), conf.get("project"))

        try:
            project = ProjectBuilder(workdir, project_name, "/etc/uji/%s/app.properties" % project_name) \
                .with_subversion(svn_web_repository, version) \
                .with_maven() \
                .with_tomcat( { "start_tomcat_after_deploy" : True }) \
                .with_validation_rules(rules) \
                .build() \
                .deploy()
        except SystemExit as e:
            flask.current_app.logger.error(traceback.format_exc())
            return "faillll"

        logger.info("Finished succesfully!!")
    except SVNException as e:
        logger.error("Invalid or unauthorized SVN repository "" + PROJECT_NAME + """)
        return "fail :("

    except ProjectIdNotFoundException as e:
        logger.error("ProjectID not found in Tomcat")
        return "fail :("

    except Exception as e:
        flask.current_app.logger.error(traceback.format_exc())
        return "fail :("

    return  "ole :)"
