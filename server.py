import flask
import threading
<<<<<<< HEAD
=======
from flask.ext.socketio import SocketIO, emit
>>>>>>> Utilizamos Flask-SocketIO para arrancar el proyecto
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
app.config['SECRET_KEY'] = 'secretor!!#!'
socketio = SocketIO(app)

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


@socketio.on('connect', namespace='/deploy')
def deploy_connect():
    stream = ShipLogger.get_memory_stream()
    stream.truncate(0)

@socketio.on('received event', namespace='/deploy')
def deploy_received(data):
    print data

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
