import flask
from commons.apps_configuration import AppsConfiguration
from commons.config import Config

conf_app = flask.Blueprint('conf_app', __name__, template_folder='../templates')
config = Config()

deploy_config = config.get('deploy')

@conf_app.route("/")
def page_apps():
    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    conf = apps_conf.get()
    return flask.render_template('configuration.html', section="conf", conf=conf, user=flask.g.get('user'))


@conf_app.route("/<app>", methods=['GET'])
def app_config(app):
    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    return apps_conf.serialize_app(app)


@conf_app.route("/<app>", methods=['PUT'])
def app_config_save(app):
    props = flask.request.form.get("props")

    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    apps_conf.save_app(app, props)

    return props


@conf_app.route("/<app>", methods=['POST'])
def new_app(app):
    host = flask.request.form.get("host")

    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    apps_conf.new(app, host)

    return 'ok'


@conf_app.route("/<app>", methods=['DELETE'])
def delete_app(app):
    apps_conf = AppsConfiguration(deploy_config.get("etcd_environment_url"))
    apps_conf.delete(app)

    return 'ok'
