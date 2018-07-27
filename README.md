# SUIT/OTA test server

## About

See https://github.com/riot-appstore/internal/issues/82 for requirements and
general development philosopy.

## Usage

This package installs a script called `ota-suit-server`.

To run in Docker:

docker build -t otaserver .
docker run -p 4000:80 otaserver

To install package using pip:

mkdir foo
python -m venv foo
. foo/bin/activate
pip install git+https://github.com/riot-appstore/ota-suit-test-server.git@proper-packaging
