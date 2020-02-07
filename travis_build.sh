#!/bin/sh
cd $TRAVIS_BUILD_DIR/src/kibana/tests/
coverage run -m unittest discover