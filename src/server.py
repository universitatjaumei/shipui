# Parcheamos las funciones bloqueantes para hacerlas compatibles con websockets
from gevent import monkey
monkey.patch_all()

import flask
import threading
from flask.ext.socketio import SocketIO, emit
from routes.deploy import deploy_app
from routes.configuration import conf_app
from routes.properties import properties_app
from routes.api import api_app
from commons.config import Config
from commons.flask_lsm_auth import LSM
import logging
import sys
import io
import time
import StringIO
import time
from ship.logger import ShipLogger
from commons.log_emitter import LogEmitter

config = Config()
webserver_config = config.get('webserver')
app = flask.Flask("shipui")
app.config['SECRET_KEY'] = webserver_config.get('websockets_secret_key')
socketio = SocketIO(app)

app.register_blueprint(api_app, url_prefix='/api')
app.register_blueprint(deploy_app, url_prefix='/deploy')
app.register_blueprint(conf_app, url_prefix='/conf')
app.register_blueprint(properties_app, url_prefix='/properties')

@app.route("/", methods=["GET"])
def index():
    return flask.redirect("/deploy")


@app.route("/logout", methods=["GET"])
def logout():
    lsm.logout(flask.request.url_root)
    return lsm.compose_response()

@app.before_request
def before_request():
    lsm = LSM(webserver_config)
    flask.g.user = lsm.get_login()

@app.after_request
def after_request(res):
    lsm = LSM(webserver_config)
    if not lsm.get_login():
        lsm.login()
    return lsm.compose_response(res)


@socketio.on('connect', namespace='/deploy')
def deploy_connect():
    stream = ShipLogger.get_memory_stream()
    stream.truncate(0)

@socketio.on('clear-log', namespace='/deploy')
def deploy_clear_log(data):
    stream = ShipLogger.get_memory_stream()
    stream.truncate(0)

@socketio.on('disconnect', namespace='/deploy')
def deploy_disconnect():
    pass


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
        # Start a new thread which sends the log by websockets
        t = LogEmitter(app, socketio)
        t.start()

        socketio.run(app, host="0.0.0.0", debug=True)
    except KeyboardInterrupt:
        t.join()
        print "bye"
