FROM debian:jessie-backports
MAINTAINER Ricardo Borillo <borillo@gmail.com>
MAINTAINER David Rubert <david.rubert@gmail.com>

RUN apt-get update -y && apt-get install --no-install-recommends -y -q python-setuptools build-essential python-dev fabric python-yaml python-simplejson subversion openjdk-8-jdk maven ca-certificates
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# Access keys
RUN mkdir /root/.ssh; chmod 600 /root/.ssh
ADD id_rsa /root/.ssh/id_rsa

# Maven repositories
ADD m2 /root/.m2

# Subversion access
ADD subversion /root/.subversion

# Install pip
RUN easy_install pip

# Install requirements.txt
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

EXPOSE 5000

VOLUME ["/src"]
WORKDIR /src

ENTRYPOINT ["python", "/src/server.py"]
CMD ["runserver"]
