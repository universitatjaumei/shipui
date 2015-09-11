import flask
from routes.deploy import deploy_app
from routes.configuration import conf_app
from routes.properties import properties_app

app = flask.Flask(__name__)
app.register_blueprint(deploy_app)
app.register_blueprint(conf_app)
app.register_blueprint(properties_app)

@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
