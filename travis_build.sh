#!/bin/sh
cd $TRAVIS_BUILD_DIR/src/data/kibana/tests/
coverage run -m pytest
