import threading
from ship.logger import ShipLogger
import time
import sys
import gevent

class LogEmitter(threading.Thread):
    def __init__(self, app, socketio, name='StoppableThread'):
        """ constructor, setting initial variables """
        self.app = app
        self.socketio = socketio
        self._stopevent = threading.Event( )
        self._sleepperiod = 3.0
        threading.Thread.__init__(self, name=name)

    def run(self):
        with self.app.test_request_context('/'):
            stream = ShipLogger.get_memory_stream()
            logger = ShipLogger()

            logger.info("hola " + str(time.time()))

            while not self._stopevent.isSet( ):
                print self._stopevent.isSet()
                line = stream.getvalue()
                if line:
                    self.socketio.emit('deploy-log', {'data': line + "\n"}, namespace='/deploy')

                gevent.sleep(self._sleepperiod)

    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)
