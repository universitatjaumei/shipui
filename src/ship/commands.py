import fabric.operations
import fabric.api
import fabric.utils
import fabric.contrib.files

DEBUG = False

def set_environment(environment, type):
    if type == "webapp":
        fabric.api.env.host_string = environment.get_tomcat_remote_connection_string()
        fabric.api.env.port = environment.get_tomcat_connection_port()

    if type == "service":
        fabric.api.env.host_string = environment.get_service_remote_connection_string()
        fabric.api.env.port = environment.get_service_connection_port()

def _get_level(debug):
    if DEBUG:
        level = fabric.api.show('everything')
    else:
        level = fabric.api.hide('everything')

    return level

def _get_settings():
    settings_dict = {"warn_only": True}
    return fabric.api.settings(_get_level(DEBUG), **settings_dict)

def local(command):
    with _get_settings():
        return fabric.operations.local(command, capture=True)

def run(command, pty=True):
    with _get_settings():
        return fabric.operations.run(command, pty=pty)

def put(local_path, remote_path):
    with _get_settings():
        return fabric.operations.put(local_path=local_path, remote_path=remote_path)

def puts(text):
    fabric.utils.puts(text)

def get(remote_path, local_path):
    fabric.api.get(remote_path=remote_path, local_path=local_path)

def abort(msg):
    fabric.utils.abort(msg)

def directory_exists(dirname):
    return fabric.contrib.files.exists(dirname)

def sudo(command):
    with _get_settings():
        return fabric.operations.sudo(command)

if __name__== "__main__":
    fabric.api.env.host_string = "root@localhost"
    fabric.api.env.port = 2222

    fabric.operations.run("ls /etc")
