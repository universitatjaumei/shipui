from __future__ import with_statement
from tomcat import Tomcat
from monit import Monit
from environment import Environment
from commands import set_environment
from validator import ValidationRuleExecutor
from validator import JDBCUrlRemoteCheck
from logger import ShipLogger
import traceback

class TomcatDeployer:
    def __init__(self, environment, params):
        self.environment = environment

        if 'tomcat' in params:
            self.params = params['tomcat']
        else:
            self.params = {}

    def deploy(self, module):
        tomcat = Tomcat(self.environment)

        tomcat.deploy(module)
        tomcat.shutdown()

        if not 'start_tomcat_after_deploy' in self.params or self.params['start_tomcat_after_deploy']:
            tomcat.startup()

class MonitDeployer:
    def __init__(self, environment, params):
        self.environment = environment
        self.logger = ShipLogger()

        if 'monit' in params:
            self.params = params['monit']
        else:
            self.params = {}

    def deploy(self, module):
        monit = Monit(self.environment.get_service_base())
        monit.shutdown_service(module)
        monit.deploy(module)
        monit.startup_service(module)

class DeployerFactory:
    _deployers = {
        "webapp": TomcatDeployer,
        "service": MonitDeployer
    }

    @staticmethod
    def build(type, environment, params):
        return DeployerFactory._deployers[type](environment, params)


class Deployer:
    def __init__(self, project):
        self.project = project
        self.deploy_params = self.project.deploy_params
        self.validations = ValidationRuleExecutor([JDBCUrlRemoteCheck])
        self.logger = ShipLogger()

    def validate(self):
        try:
            self.validations.validate(self.project)
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise(e)

    def _deploy(self, module, environment, params):
        deployer = DeployerFactory.build(module.get_type(), environment, params)
        deployer.deploy(module)

    def deploy(self):
        for module in self.project.get_modules():
            deploy_environment = Environment(self.project.get_name())
            set_environment(deploy_environment, module.get_type())
            self.validate()
            self._deploy(module, deploy_environment, self.deploy_params)
