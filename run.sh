#!/bin/bash
pushd `dirname $0` > /dev/null

docker rm -f shipui
bower install
docker build -t ship/shipui .
docker run -d -p 5000:5000 -v /opt/devel/workspaces/uji/shipui/root:/root --name shipui ship/shipui
#docker run -d -p 5000:5000 -v /opt/devel/workspaces/uji/shipui/src:/src -v /opt/devel/workspaces/uji/shipui/root:/root --name shipui ship/shipui

popd > /dev/null
