import os, shutil

from logger import ShipLogger
from commands import local
from errors import SVNException

class Subversion:

    def __init__(self, url, home, project, version="trunk"):
        self.url = url
        self.home = home
        self.project = project
        self.version = version
        self.logger = ShipLogger()

    def get_tags(self):
        tagsList= local("svn list " + self.url + "/tags").split("\n")
        tags = map(lambda x: x.replace("/", ""), tagsList)
        return tags

    def checkout(self):
        self.logger.info("Checking out %s version from source control" % self.version)

        if os.path.isdir(self.home):
            self.logger.warning("Cleaning work directory. Existing dir found")
            shutil.rmtree(self.home)

        if self.version == "trunk":
            result = local("svn co " + self.url + "/" + self.version + " " + self.home + "/" + self.project)
        else:
            result = local("svn co " + self.url + "/tags/" + self.version + " " + self.home + "/" + self.project)

        if result.return_code != 0:
            self.logger.error("Project repository not found in SVN with URL %s" % self.url)
            raise SVNException()

if __name__ == "__main__":
    subversion = Subversion("svn://localhost/repos/SAMPLE", "/tmp/SAMPLE")
    subversion.checkout()
