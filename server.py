import flask
import threading
from routes.deploy import deploy_app
from routes.configuration import conf_app
from routes.properties import properties_app
import logging
import sys
import io
import time
import flask_lsm_auth
import StringIO
import time
from ship.logger import ShipLogger
from commons.log_emitter import LogEmitter

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

@app.after_request
def after_request(res):
    lsm = flask_lsm_auth.LSM()
    if not lsm.get_login():
        lsm.login()

    return lsm.compose_response(res)


@app.before_first_request
def setup_logging():
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.INFO)

    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[shipui] %(levelname)s %(message)s"))
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

if __name__ == "__main__":

    try:
        app.run(host="0.0.0.0", debug=True)
    except KeyboardInterrupt:
        t.join()
        print "bye"
