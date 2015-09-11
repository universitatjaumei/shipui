import requests
import codecs
import os

URL = 'http://conf.uji.es/v2/keys/ujiapps/apps/%s/app.properties'

class AppsProperties:

    def __init__(self, app):
        self.app = app

    def get(self):
        #r = requests.get(URL % self.app)
        r = requests.get(URL % 'adc')
        data = r.json()
        return data["node"]["value"]

    def create_app_properties_directory(self):
        try:
            os.makedirs("/etc/uji/%s" % self.app)
        except Exception as e:
            pass

    def save_todisk(self):
        self.create_app_properties_directory()
        with codecs.open("/etc/uji/%s/app.properties" % self.app, "w+", "utf-8") as properties_file:
            properties_file.write(self.get())


if __name__ == "__main__":
    app = AppsProperties("apa")
    print app.get()
