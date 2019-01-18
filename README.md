# SUIT/OTA test server

See https://github.com/riot-appstore/internal/issues/82 for requirements and
general development philosopy.

## Usage

This package installs an ota security microservice. Currently in PoC state.

To run in Docker:

docker build -t otaserver .
sh start.sh
