import flask
from routes.deploy import deploy_app
from routes.configuration import conf_app
from routes.properties import properties_app
import logging
import sys

app = flask.Flask("shipui")

app.register_blueprint(deploy_app)
app.register_blueprint(conf_app)
app.register_blueprint(properties_app)

@app.route("/", methods=["GET"])
def index():
    return flask.render_template("index.html")


def setup_log():
    logger = logging.getLogger("werkzeug")
    handler = logging.StreamHandler()
    handler.setLevel(logging.getLevelName("INFO"))
    handler.setFormatter(logging.Formatter("[shipui] %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


if __name__ == "__main__":

    setup_log()
    app.run(host="0.0.0.0", debug=True)
