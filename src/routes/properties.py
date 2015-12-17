import flask
from commons.apps_properties import AppsProperties
import flask_lsm_auth

properties_app = flask.Blueprint('properties_app', __name__, template_folder='../templates')

@properties_app.route("/properties")
def page_apps():
    lsm = flask_lsm_auth.LSM()
    return flask.render_template('properties.html', section="properties", user=lsm.get_login())


@properties_app.route("/properties/<app>", methods=['GET'])
def app_config(app):
    apps_properties = AppsProperties(app)
    return apps_properties.get()


@properties_app.route("/properties/<app>", methods=['PUT'])
def app_config_save(app):
    props = flask.request.form.get("props")

    apps_properties = AppsProperties(app)
    apps_properties.save(props)

    return props


@properties_app.route("/properties/<app>", methods=['POST'])
def new_app(app):
    host = flask.request.form.get("host")

    apps_properties = AppsProperties(app)
    apps_properties.new()

    return 'ok'


@properties_app.route("/properties/<app>", methods=['DELETE'])
def delete_app(app):
    apps_properties = AppsProperties(app)
    apps_properties.delete(app)

    return 'ok'
