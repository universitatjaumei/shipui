class Module:
    def __init__(self, project, module_type, packaging, final_name, version, submodule=None):
        self.project = project
        self.type = module_type
        self.packaging = packaging
        self.final_name = final_name
        self.version = version
        self.submodule = submodule

    def get_version(self):
        return self.version

    def get_type(self):
        return self.type

    def get_packaging(self):
        return self.packaging

    def get_submodule(self):
        return self.submodule

    def get_name(self):
        return self.final_name

    def get_directory(self):
        dir = self.project.get_directory()

        if self.submodule != None:
           dir = dir + "/" + self.submodule

        return dir
