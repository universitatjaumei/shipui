URL = 'http://conf.uji.es/v2/keys/ujiapps/apps/all.yaml'

import requests
import yaml

class AppsConfiguration:
    def get(self):
        r = requests.get(URL)
        data = r.json()
        yaml_content = data["node"]["value"]

        return yaml.load(yaml_content)

    def serialize_app(self, app):
        return yaml.dump(self.get()[app], default_flow_style=False)

    def save(self, conf):
        data = yaml.dump(conf, default_flow_style=False)
        requests.put(URL, data={"value": data})

    def save_app(self, app, data):
        new_app_conf = yaml.load(data)
        conf = self.get()

        conf[app] = new_app_conf
        self.save(conf)

    def save_todisk(self):
        with open("environment.yml", "w+") as yaml_file:
            yaml_file.write(yaml.dump(self.get(), default_flow_style=False))

    def new(self, app, host):
        conf = self.get()

        if conf.has_key(app):
            raise Exception("App already exists")

        new_config = """%s:
  host: %s
  java: 8
  port: 22
  user: aplicacions
  tomcat:
    base: /mnt/data/aplicacions/server/tomcat
    memory: 198
    version: 8.0.22
    username: tomcat
    password: tomcat
    ports:
      ajp: 6124
      http: 8124
      jmx: 9624
      redirect: 9124
      shutdown: 7124""" % (app, host)

        conf[app] = yaml.load(new_config)
        self.save(conf)

    def delete(self, app):
        conf = self.get()
        conf.pop(app, None)

        self.save(conf)
