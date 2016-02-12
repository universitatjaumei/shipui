import flask
from commons.apps_configuration import AppsConfiguration
from commons.config import Config

api_app = flask.Blueprint('api_app', __name__, template_folder='../templates')

config = Config()
deploy_config = config.get('deploy')

@api_app.route("/apps", methods=['GET'])
def all_apps():
    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    return flask.jsonify(apps_conf.get())
