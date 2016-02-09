import requests
import yaml

class AppsConfiguration:
    def __init__(self, url):
        self.url = url

    def get(self):
        r = requests.get(self.url)
        data = r.json()
        yaml_content = data["node"]["value"]

        return yaml.load(yaml_content)

    def getByPath(self, path):
        config = self.get()

        for key in config.keys():
            if config[key].get("path") == path:
                return config[key]

    def get_applications(self):
        config = self.get()
        result = []

        keys = config.keys()
        keys.sort()
        for key in keys:
            if 'path' in config[key]:
                result.append({ 'name': key.upper(), 'alternative':config[key]['path'].upper() })
            else:
                result.append({ 'name': key.upper(), 'alternative': key.upper() })

        return result

    def serialize_app(self, app):
        return yaml.safe_dump(self.get()[app], default_flow_style=False)

    def save(self, conf):
        data = yaml.safe_dump(conf, default_flow_style=False)
        requests.put(self.url, data={"value": data})

    def save_app(self, app, data):
        new_app_conf = yaml.load(data)
        conf = self.get()

        conf[app] = new_app_conf
        self.save(conf)

    def save_todisk(self):
        with open("environment.yml", "w+") as yaml_file:
            yaml_file.write(yaml.safe_dump(self.get(), default_flow_style=False))

    def get_next_port_offset(self, conf):
        next_port_offset = 0
        for key, value in conf.items():
            port = value.get("tomcat").get("ports").get("http")
            offset = port - int(port/100)*100

            if offset > next_port_offset:
                next_port_offset = offset


        return next_port_offset + 1

    def new(self, app, host):
        conf = self.get()

        if conf.has_key(app):
            raise Exception("App already exists")

        port = self.get_next_port_offset(conf)

        app_data = {
            "project": "uji-" + app,
            "host": host,
            "ajp": 6100 + port,
            "http": 8100 + port,
            "jmx": 9600 + port,
            "redirect": 9100 + port,
            "shutdown": 7100 + port
        }

        new_config = """
java: 8
project: %(project)s
tomcat:
  admin:
    password: infrapod136
    username: tomcat
  base: /mnt/data/aplicacions/server/tomcat
  connection:
    host: %(host)s
    port: 22
    type: ssh
    username: aplicacions
  memory: 198
  ports:
    ajp: %(ajp)s
    http: %(http)s
    jmx: %(jmx)s
    redirect: %(redirect)s
    shutdown: %(shutdown)s
  version: 8.0.22""" % app_data

        conf[app] = yaml.load(new_config)
        self.save(conf)

    def delete(self, app):
        conf = self.get()

        conf.pop(app, None)

        self.save(conf)

if __name__ == "__main__":
    app = AppsConfiguration()
    with open("environment.yml", "r") as stream:
        y = yaml.load(stream)
        d = yaml.dump(y, default_flow_style=False)

        print d
        # Write Full file into etcd
        requests.put(self.url, data={"value": d})
