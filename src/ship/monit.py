from logger import ShipLogger
from commands import *
from time import sleep
import os.path
import re


class Monit:

    def __init__(self, home):
        self.home = home
        self.logger = ShipLogger()

    def get_deploy_directory(self, service_name):
        return os.path.join(self.home, service_name, service_name + ".jar")

    def startup_service(self, module):
        appname = module.get_name()
        run("sudo /usr/bin/monit -c /etc/monit.conf start " + appname)

        times = 1
        while not self._running(appname) and times < 30:
            sleep(10)
            puts(".")
            times = times + 1
            self.logger.info("Trying to start the service ...")

        if not self._running(appname):
            error_message = "Can not complete the service '%s' restart" % appname
            self.logger.error(error_message)
            abort(error_message)

        self.logger.info("Monit startup process completed")

    def shutdown_service(self, module):
        run("sudo /usr/bin/monit -c /etc/monit.conf stop " + module.get_name())

    def deploy(self, module):
        appname = module.get_name()
        jarfile = "%s/target/%s.jar" % (module.get_directory(), appname)

        self.logger.info("Copying JAR of module '" + appname + "' to remote host: %s" % self.get_deploy_directory(appname))
        put(local_path=jarfile, remote_path=self.get_deploy_directory(appname))

    def _running(self, name):
        res = run("sudo /usr/bin/monit -c /etc/monit.conf status")
        res = res.split("\r\n")

        index = res.index("Process '%s'" % name)
        status = res[index + 1].strip()
        status = re.sub(' +', ' ', status)

        return status.split()[1] == 'Running'


if __name__ == "__main__":
    from environment import Environment
    deploy_environment = Environment("development", "uji-ade-bd2storage")
    set_environment(deploy_environment)
    monit = Monit("/mnt/data/aplicacions/cron/")
    print monit._running("uji-ade-bd2storage")
    monit.shutdown_service("uji-ade-bd2storage")
    monit.deploy(
        "/opt/devel/workspaces/uji/uji-deployment-tools/deploy/target/ADE/uji-ade/uji-ade-bd2storage/target/uji-ade-bd2storage.jar", "uji-ade-bd2storage")
    monit.startup_service("uji-ade-bd2storage")
