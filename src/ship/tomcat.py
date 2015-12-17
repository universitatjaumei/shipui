from logger import ShipLogger
from time import sleep, strftime
from commands import *
import base64


class Tomcat:

    def __init__(self, config):
        self.host = config.get_tomcat_host()
        self.home = config.get_tomcat_home()
        self.base = config.get_tomcat_base()
        self.version = config.get_tomcat_version()

        self.user = config.get_tomcat_username()
        self.password = config.get_tomcat_password()

        self.http_port = config.get_tomcat_http_port()
        self.ajp_port = config.get_tomcat_ajp_port()
        self.jmx_port = config.get_tomcat_jmx_port()
        self.redirect_port = config.get_tomcat_redirect_port()
        self.shutdown_port = config.get_tomcat_shutdown_port()

        self.deploy_dir = config.get_tomcat_deploy_directory()
        self.memory = config.get_tomcat_memory()

        self.logger = ShipLogger()


    def startup(self):
        result = run(self.home + "/bin/startup.sh", pty=False)

        if result.return_code != 0:
            error_message = "The server could not be started"
            self.logger.error(error_message)
            abort(error_message)
            return

        times = 1

        while not self._running() and times < 10:
            sleep(10)
            times += 1
            self.logger.info("Trying to start the tomcat server...")


        if times == 10:
            error_message = "Can not complete the server startup"
            self.logger.error(error_message)
            abort(error_message)

        self.logger.info("Tomcat startup process completed")

    def shutdown(self):
        try:
            result = run(self.home + "/bin/shutdown.sh -force")
        except Exception as e:
            pass

    def deploy(self, module):
        appname = module.get_name()
        warfile = "%s/target/%s.war" % (module.get_directory(), appname)

        run("rm -rf " + self.home + "/work")
        run("rm -rf " + self.home + "/webapps/" + appname)

        self.logger.info("Copying WAR of module '" + appname + "' to remote host: %s" % self.deploy_dir)
        put(local_path=warfile, remote_path=self.deploy_dir)

    def install(self):
        current_date = strftime("%Y%m%d-%H%M%S")

        run("wget -q http://static.uji.es/services/docker/apache-tomcat-%s.tar.gz -O /tmp/tomcat.tar.gz" % self.version)
        run("tar xfz /tmp/tomcat.tar.gz -C %s" % self.base)
        run("mv %s/apache-tomcat-%s %s" % (self.base, self.version, self.home))
        run("rm /tmp/tomcat.tar.gz")

        # configure_javahome_startup

        for filename in ["startup.sh", "shutdown.sh"]:
            remote_file = "%s/bin/%s" % (self.home, filename)
            local_file = "/tmp/%s.%s" % (filename, current_date)

            get(remote_file, local_file)

            file = open(local_file, "r")
            content = file.readlines()
            file.close()

            content.insert(21, "export JAVA_HOME=/mnt/data/aplicacions/sdk/jdk1.8.0_45\nexport PATH=$JAVA_HOME/bin:$PATH\n\n")

            file = open(local_file, "w")
            file.write("".join(content))
            file.close()

            put(local_file, remote_file)

        # configure_tomcat_env

        file = open("/tmp/setenv.sh.%s" % current_date, "w")
        file.write("#!/bin/sh\n\n")
        file.write("export LC_ALL=\"es_ES.UTF-8\"\n")
        file.write("export LANG=\"es_ES.UTF-8\"\n")
        file.write("export JAVA_OPTS=\"%s -Dfile.encoding=UTF-8 -XX:+CMSClassUnloadingEnabled\"\n" % self.memory)
        file.write("export CATALINA_PID=$CATALINA_BASE/tomcat.pid\n")
        file.write("export CATALINA_OPTS=\"-Djava.awt.headless=true -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=%s -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false\"\n" % self.jmx_port)
        file.close()

        put("/tmp/setenv.sh.%s" % current_date, "%s/bin/setenv.sh" % self.home)

        run("chmod u+x %s/bin/setenv.sh" % self.home)

        # configure_tomcat

        file = open("/tmp/server.xml.%s" % current_date, "w")
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        file.write("<Server port=\"%s\" shutdown=\"SHUTDOWN\">\n" % self.shutdown_port)
        file.write("  <Listener className=\"org.apache.catalina.startup.VersionLoggerListener\" />\n")
        file.write("  <Listener className=\"org.apache.catalina.core.AprLifecycleListener\" SSLEngine=\"on\" />\n")
        file.write("  <Listener className=\"org.apache.catalina.core.JreMemoryLeakPreventionListener\" />\n")
        file.write("  <Listener className=\"org.apache.catalina.mbeans.GlobalResourcesLifecycleListener\" />\n")
        file.write("  <Listener className=\"org.apache.catalina.core.ThreadLocalLeakPreventionListener\" />\n\n")
        file.write("  <GlobalNamingResources>\n")
        file.write("    <Resource name=\"UserDatabase\" auth=\"Container\"\n")
        file.write("              type=\"org.apache.catalina.UserDatabase\"\n")
        file.write("              description=\"User database that can be updated and saved\"\n")
        file.write("              factory=\"org.apache.catalina.users.MemoryUserDatabaseFactory\"\n")
        file.write("              pathname=\"conf/tomcat-users.xml\" />\n")
        file.write("  </GlobalNamingResources>\n\n")
        file.write("  <Service name=\"Catalina\">\n")
        file.write("    <Connector port=\"%s\" protocol=\"HTTP/1.1\" connectionTimeout=\"20000\" redirectPort=\"%s\" URIEncoding=\"UTF-8\" />\n" %
                   (self.http_port, self.redirect_port))
        file.write("    <Connector port=\"%s\" protocol=\"AJP/1.3\" redirectPort=\"%s\" URIEncoding=\"UTF-8\" />\n\n" %
                   (self.ajp_port, self.redirect_port))
        file.write("    <Engine name=\"Catalina\" defaultHost=\"localhost\">\n")
        file.write("      <Realm className=\"org.apache.catalina.realm.LockOutRealm\">\n")
        file.write("        <Realm className=\"org.apache.catalina.realm.UserDatabaseRealm\" resourceName=\"UserDatabase\"/>\n")
        file.write("      </Realm>\n\n")
        file.write("      <Host name=\"localhost\" appBase=\"webapps\" unpackWARs=\"true\" autoDeploy=\"false\">\n")
        file.write("        <Valve className=\"org.apache.catalina.valves.AccessLogValve\" directory=\"logs\"\n")
        file.write("               prefix=\"localhost_access_log\" suffix=\".txt\"\n")
        file.write("               pattern=\"%h %l %u %t &quot;%r&quot; %s %b\" />\n")
        file.write("      </Host>\n")
        file.write("    </Engine>\n")
        file.write("  </Service>\n")
        file.write("</Server>")
        file.close()

        put("/tmp/server.xml.%s" % current_date, "%s/conf/server.xml" % self.home)

    def uninstall(self):
        if not directory_exists(self.home): return

        current_date = strftime("%Y%m%d-%H%M%S")

        self.shutdown()

        run("mv %s /tmp/%s.%s" % (seself.home, self.home.split("/")[-1], current_date))

    def _running(self):
        try:
            url = "http://%s:%s/manager/text/list" % (self.host, self.http_port)
            hashed_password = base64.b64encode("%s:%s" % (self.user, self.password))

            data = run("curl -H 'Authorization: Basic %s' %s" % (hashed_password, url))
            return data[:4] == "OK -"
        except:
            import traceback
            print traceback.format_exc()

            return False


# def activate_redis_sessions(app, config):
#     catalina_home = BASE + "/" + app
#
#     local(
#         "wget -q http://static.uji.es/services/docker/redis-store-1.3.0.BUILD-SNAPSHOT.jar -O %s/lib/redis-store-1.3.0.BUILD-SNAPSHOT.jar" % catalina_home)
#
#     file = open("%s/conf/context.xml" % catalina_home, "w")
#     file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
#     file.write("<Context>\n")
#     file.write("  <WatchedResource>WEB-INF/web.xml</WatchedResource>\n")
#     file.write("  <WatchedResource>${catalina.base}/conf/web.xml</WatchedResource>\n")
#     file.write("  <Valve className=\"com.gopivotal.manager.SessionFlushValve\" />\n")
#     file.write("  <Manager className=\"org.apache.catalina.session.PersistentManager\">\n")
#     file.write("    <Store className=\"com.gopivotal.manager.redis.RedisStore\" host=\"infra01.uji.es\" />\n")
#     file.write("  </Manager>\n")
#     file.write("</Context>")
#     file.close()
#
#
# def configure_tomcat_access_manager(app, config):
#     catalina_home = BASE + "/" + app
#
#     file = open("%s/conf/tomcat-users.xml" % catalina_home, "w")
#     file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
#     file.write("<tomcat-users>\n")
#     file.write("  <role rolename=\"manager-gui\"/>\n")
#     file.write("  <role rolename=\"manager-script\"/>\n")
#     file.write("  <user username=\"tomcat\" password=\"infrapod136\" roles=\"manager-gui, manager-script\"/>\n")
#     file.write("</tomcat-users>\n")
#     file.close()
#
# if __name__ == "__main__":
#     fabric.api.env.host_string = "borillo@aris.si.uji.es"
#     fabric.api.env.password = "heroes2000"
#
#     app = "apa"
#     config = ujiapps["apexp02.uji.es"][app]
#
#     clear_if_exists(app, config)
#
#     install_tomcat(app, config)
#     configure_javahome_startup(app, config)
#     configure_tomcat_env(app, config)
#     activate_redis_sessions(app, config)
#     configure_tomcat_access_manager(app, config)
#     configure_tomcat(app, config)
