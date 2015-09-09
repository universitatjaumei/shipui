import flask
from config import AppsConfiguration
from ship.logger import ShipLogger
from ship.project import ProjectBuilder
from ship.validator import *
from ship.errors import SVNException, ProjectIdNotFoundException
import urllib2
import yaml
import simplejson
import traceback

app = flask.Flask(__name__)


@app.route("/")
def page_apps():
    apps_conf = AppsConfiguration()
    conf = apps_conf.get()
    return flask.render_template('apps.html', conf=conf)


@app.route("/conf", methods=['GET'])
def all_apps():
    apps_conf = AppsConfiguration()
    return flask.jsonify(apps_conf.get())


@app.route("/conf/<app>", methods=['GET'])
def app_config(app):
    apps_conf = AppsConfiguration()
    return apps_conf.serialize_app(app)


@app.route("/conf/<app>", methods=['PUT'])
def app_config_save(app):
    props = flask.request.form.get("props")

    apps_conf = AppsConfiguration()
    apps_conf.save_app(app, props)

    return props


@app.route("/conf/<app>", methods=['POST'])
def new_app(app):
    host = flask.request.form.get("host")

    apps_conf = AppsConfiguration()
    apps_conf.new(app, host)

    return 'ok'


@app.route("/conf/<app>", methods=['DELETE'])
def delete_app(app):
    apps_conf = AppsConfiguration()
    apps_conf.delete(app)

    return 'ok'


def get_app_acronyms():
    req = urllib2.Request("http://infra01.uji.es:4001/v2/keys/ujiapps/apps/all.yaml")
    response = urllib2.urlopen(req)
    data = simplejson.load(response)
    yaml_text = data.get('node').get('value')
    data = yaml.load(yaml_text)
    apps = [ app.upper() for app in data.keys() ]
    apps.sort()
    return apps

@app.route("/deploy", methods=["GET"])
def index():
    apps = get_app_acronyms()
    return flask.render_template("deploy.html", apps=apps)


@app.route("/deploy", methods=["POST"])
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



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
