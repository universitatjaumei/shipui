import yaml

class ShipUIConfig:
    def __init__(self):
        f = open("config.yml")
        data = yaml.safe_load(f)
        self.data = data.get("deploy")
        f.close()

    def get(self, key):
        return self.data.get(key)
