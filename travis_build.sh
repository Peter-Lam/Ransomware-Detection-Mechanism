#!/bin/sh
cd $TRAVIS_BUILD_DIR/src/utils/tests/
coverage run -m pytest
