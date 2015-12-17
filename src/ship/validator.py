import os
import logging
from commands import local
from commands import run
from xml.dom import minidom
from colors import Colors

class PomXMLValidationRule:
    def execute(self, project, module):
        if module.get_type() in ['webapp', 'service']:
            if not module.get_name():
                raise Exception("The 'finalName' attribute couldn't be found in pom.xml file")
        else:
            raise Exception("The module type '" + module.get_type() + "' is not valid.'")

class JDBCUrlRemoteCheck:
    def execute(self, project, environment):
        app_properties = run("cat /etc/uji/%s/app.properties" % project.get_name())
        JDBCURL = """uji.db.jdbcUrl=jdbc:oracle:thin:@(DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(HOST = 150.128.192.222)(PORT = 1521)) (ADDRESS = (PROTOCOL = TCP)(HOST = 150.128.192.223)(PORT = 1521)) (ADDRESS = (PROTOCOL = TCP)(HOST = 150.128.192.224)(PORT = 1521)) (LOAD_BALANCE = yes) (FAILOVER = yes)) (CONNECT_DATA = (SERVICE_NAME = ujiapps.uji.es)))"""

        if app_properties.find(JDBCURL) == -1:
            raise Exception("The JDBCUrl syntax in remote environment /etc/uji/%s/app.properties is not valid." % project.get_name())

class ConsoleLogValidationRule:
    def execute(self, project, module):
        if module.get_type() == 'webapp':
            rootdir = "%s/src/main/webapp" % module.get_directory()

            for root, dirs, files in os.walk(rootdir):
                for file in files:
                    if self.isJavascript(file) and self.fileHasConsoleLog(os.path.join(root, file)):
                        raise Exception("The file %s has console.log commands inside." % os.path.join(root, file))

    def isJavascript(self, file):
        return file.find(".js") == len(file) - 3

    def fileHasConsoleLog(self, file):
        with open(file) as f:
            for line in f.xreadlines():
                if line.find("console.log") != -1:
                    return True

        return False

class ConfigFileValidationRule:
    def execute(self, project, module):
        app_properties = project.get_config()

        if not os.path.isfile(app_properties) or not os.access(app_properties, os.R_OK):
            raise Exception("Can't read %s file or does not exists" % app_properties)

        try:
            lines = open(app_properties).readlines()
        except:
            raise Exception("Please convert %s to utf-8" % app_properties)

        needles = {
            "uji.deploy.returnScheme=": False,
            "uji.deploy.returnHost=ujiapps": False,
            "uji.deploy.returnPort=": False
        }

        for line in lines:
            line = line.strip()

            for needle in needles.keys():
                if line.find(needle) == 0:
                    needles[needle] = True

        for needle, found in needles.items():
            if not found:
                raise Exception("The value of %s is not set properly for production deploy on %s file." % (needle, app_properties))

class CompiledPackageExistsValidationRule:
    def execute(self, project, module):

        if project.is_multimodule():
            if module.get_type() == "webapp":
                path = project.get_directory() + "/" + module.get_submodule() + "/target/" + module.get_name() + "." + module.get_packaging()
                if not os.path.exists(path):
                    raise Exception("Compiled package %s does not exists" % path)
            elif module.get_type() == "service":
                path = project.get_directory() + "/" + module.get_submodule() + "/target/" + module.get_name() + ".jar"
                if not os.path.exists(path):
                    raise Exception("Compiled package %s does not exists" % path)

        else:
            if module.get_type() == "webapp":
                path = project.get_directory() + "/target/" + module.get_name() + "." + module.get_packaging()
                if not os.path.exists(path):
                    raise Exception("Compiled package %s does not exists." % path)


class WebXmlValidationRule:
    def execute(self, project, module):
        if module.get_type() != 'webapp':
            return

        os.mkdir("%s/target/verify" % module.get_directory())
        local("unzip -d %s/target/verify %s/target/%s.war" % (module.get_directory(), module.get_directory(), module.get_name()))

        if not os.path.isfile("%s/target/verify/WEB-INF/web.xml" % module.get_directory()):
            logging.warning(Colors.WARNING + "[WARN] web.xml file can not be found. Servlets 3.0 module?" + Colors.ENDC)
            return

        webxml = minidom.parse("%s/target/verify/WEB-INF/web.xml" % module.get_directory())

        ujiappsFilter = [node for node in webxml.getElementsByTagName("param-value") if node.childNodes[0].nodeValue == "ujiapps.uji.es"]

        if len(ujiappsFilter) != 2:
            logging.warning(Colors.WARNING + "[WARN] Missing ujiapps.uji.es reference on web.xml. Public module?" + Colors.ENDC)

        distributable = webxml.getElementsByTagName("distributable")

        if len(distributable) != 1:
            raise Exception("Missing <distributable/> element on web.xml")

        beansListener = [node for node in webxml.getElementsByTagName("listener-class") if node.childNodes[0].nodeValue == "es.uji.commons.rest.listeners.CleanUpOracleMBeansListener"]

        if len(beansListener) != 1:
            raise Exception("Must include Oracle MBean cleanup listener on web.xml")

class ValidationRuleExecutor:
    def __init__(self, validation_rules):
        self.validation_rules = validation_rules

    def validate(self, project):
        for module in project.get_modules():
            for rule in self.validation_rules:
                rule().execute(project, module)
