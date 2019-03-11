# SUIT/OTA test server

See https://github.com/riot-appstore/internal/issues/82 for requirements and
general development philosopy.

## Usage

This package installs a script called `ota-suit-server`.

To run in Docker:

docker build -t otaserver .
docker run -it --entrypoint="/bin/bash" -v $(pwd):/app -p 4000:80 otaserver
pip install --trusted-host pypi.python.org -r requirements.txt
cd app/suit-server
python main.py
