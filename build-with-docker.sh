#!/bin/bash 
export CONAN_PIP_COMMAND=pip3
export CONAN_USERNAME="disroop"
export CONAN_CHANNEL="development"
export CONAN_GCC_VERSIONS=9
export CONAN_ARCHS=armv7
export CONAN_DOCKER_IMAGE=conanio/gcc9-armv7
export CONAN_USE_DOCKER=1
export CPT_TEST_FOLDER="conan/test_package"
if [ "$PUBLISH" == True ]
then
    export CONAN_LOGIN_USERNAME=$ARTIFACTORY_USER
    export CONAN_PASSWORD=$ARTIFACTORY_PW
    export CONAN_UPLOAD="TBD" # ADJUST WITH YOUR REMOTE!
    export CONAN_UPLOAD_DEPENDENCIES="all"
fi

python3 ./build.py