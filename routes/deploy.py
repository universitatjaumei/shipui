from ship.logger import ShipLogger
from ship.project import ProjectBuilder
from ship.validator import *
from ship.errors import SVNException, ProjectIdNotFoundException
import urllib2
import yaml
import simplejson
import traceback
import flask

deploy_app = flask.Blueprint('deploy_app', __name__, template_folder='../templates')

def get_app_acronyms():
    req = urllib2.Request("http://infra01.uji.es:4001/v2/keys/ujiapps/apps/all.yaml")
    response = urllib2.urlopen(req)
    data = simplejson.load(response)
    yaml_text = data.get('node').get('value')
    data = yaml.load(yaml_text)
    apps = [ app.upper() for app in data.keys() ]
    apps.sort()
    return apps


@deploy_app.route("/deploy", methods=["GET"])
def index():
    apps = get_app_acronyms()
    return flask.render_template("deploy.html", apps=apps)


@deploy_app.route("/deploy", methods=["POST"])
def deploy():
    environment = request.args.get("environment") #"production"
    home = request.args.get("home") #"/tmp/target"
    url = request.args.get("url") #"svn://localhost/repos/SAMPLE"
    project = request.args.get("project") #"sample"
    key = request.args.get("key") #"smp"
    version = request.args.get("version") #"trunk"

    try:
        app.logger.info("Initializing project construction")

        rules = [ ConfigFileValidationRule, ConsoleLogValidationRule,
                  PomXMLValidationRule, CompiledPackageExistsValidationRule ]

        try:
            project = ProjectBuilder(HOME, PROJECT_NAME, "/etc/uji/%s/app.properties" % KEY) \
                .with_subversion(URL, VERSION) \
                .with_maven() \
                .with_validation_rules(rules) \
                .build() \
                .deploy(ENVIRONMENT)
        except SystemExit as e:
            app.logger.error(traceback.format_exc())
            return 'faillll'

        app.logger.info("Finished succesfully!!")
    except SVNException as e:
        app.logger.error("Invalid or unauthorized SVN repository '" + PROJECT_NAME + "'")
        return "fail :("

    except ProjectIdNotFoundException as e:
        app.logger.error("ProjectID not found in Tomcat")
        return "fail :("

    except Exception as e:
        app.logger.error(traceback.format_exc())
        return "fail :("

    return  "ole :)"
