import yaml
import os

class Config:
    def __init__(self):
        f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config.yml"))
        data = yaml.safe_load(f)
        self.data = data.get("shipui")
        f.close()

    def get(self, section,):
        return self.data.get(section)
