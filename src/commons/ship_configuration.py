import yaml
import os

class ShipUIConfig:
    def __init__(self):
        f = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "config.yml"))
        data = yaml.safe_load(f)
        self.data = data.get("deploy")
        f.close()

    def get(self, key):
        return self.data.get(key)
