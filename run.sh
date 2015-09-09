#!/bin/bash
pushd `dirname $0` > /dev/null

docker rm -f shipui

docker build -t ship/shipui dockerized-shipui

cp -a ../ship/ship  $(pwd)

docker run -d -p 5000:5000 -v /opt/devel/workspaces/uji/shipui:/src --name shipui ship/shipui

popd > /dev/null
