import flask
from commons.apps_configuration import AppsConfiguration
from commons.ship_configuration import ShipUIConfig
import flask_lsm_auth

conf_app = flask.Blueprint('conf_app', __name__, template_folder='../templates')
shipui_conf = ShipUIConfig()

@conf_app.route("/conf")
def page_apps():
    lsm = flask_lsm_auth.LSM()
    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    conf = apps_conf.get()
    return flask.render_template('configuration.html', section="conf", conf=conf, user=lsm.get_login())


@conf_app.route("/api/apps", methods=['GET'])
def all_apps():
    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    return flask.jsonify(apps_conf.get())


@conf_app.route("/conf/<app>", methods=['GET'])
def app_config(app):
    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    return apps_conf.serialize_app(app)


@conf_app.route("/conf/<app>", methods=['PUT'])
def app_config_save(app):
    props = flask.request.form.get("props")

    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    apps_conf.save_app(app, props)

    return props


@conf_app.route("/conf/<app>", methods=['POST'])
def new_app(app):
    host = flask.request.form.get("host")

    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    apps_conf.new(app, host)

    return 'ok'


@conf_app.route("/conf/<app>", methods=['DELETE'])
def delete_app(app):
    apps_conf = AppsConfiguration(shipui_conf.get("etcd_environment_url"))
    apps_conf.delete(app)

    return 'ok'
