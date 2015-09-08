import flask
from config import AppsConfiguration

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


if __name__ == "__main__":
    app.run(debug=True)
