import flask
from routes.deploy import deploy_app
from routes.configuration import conf_app
from routes.properties import properties_app
import logging
import sys
import flask_lsm_auth

app = flask.Flask("shipui")


app.register_blueprint(deploy_app)
app.register_blueprint(conf_app)
app.register_blueprint(properties_app)

@app.route("/", methods=["GET"])
def index():
    return flask.redirect("/deploy")

@app.route("/logout", methods=["GET"])
def logout():
    lsm = flask_lsm_auth.LSM()
    lsm.logout(flask.request.url_root)

    return lsm.compose_response()


def setup_log():
    logger = logging.getLogger("werkzeug")
    handler = logging.StreamHandler()
    handler.setLevel(logging.getLevelName("INFO"))
    handler.setFormatter(logging.Formatter("[shipui] %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

@app.after_request
def after_request(res):

    lsm = flask_lsm_auth.LSM()
    app.logger.info("Requesting %s...", flask.request.url)

    if not lsm.get_login():
        lsm.login()

    return lsm.compose_response(res)

if __name__ == "__main__":

    setup_log()
    app.run(host="0.0.0.0", debug=True)
