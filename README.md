# SUIT/OTA test server

## Overview

This provides two web pages: a "user" and an "app" page. The "user" page is
where the user creates their key pair, uploads the public key, and prepares the
device. The "app" page is where the application is deployed to the device.

Under-the-hood, the following is performed. In the "user" page, a RIOT
application image is built from a repo residing on the server. The uploaded
public key is included in this image. In the "app" page, an application image
along with its manifest is built. The manifest is transferred to the client,
signed in the client using the user's private key, and re-uploaded. The user's
private key is requested via a pop-up dialog, and doesn't leave the user's
computer. The CoAP endpoint of the device is specified by the user in the
"app" page.

## Installation

1. Clone this repo
2. Install native messaging host and browser extension in firefox according to
   instructions in
   https://github.com/riot-appstore/rapstore-browser-integration
3. Clone https://github.com/ARMmbed/suit-manifest-generator.git into this repo

## Usage

1. docker build -t otaserver .
2. sh start.sh
3. cd ../app2/suit-server (in the container)
5. python3 main.py

the web pages are available at localhost:4000/app and localhost:4000/user.

## Notes on operation

This needs to be run in Firefox for the automatic device preparation to work.
This is because the size of the flasher package is larger than that allowed by
Chrome's browser extension.

## TODOs

The RIOT repository is currently committed as part of this repo and should be
cloned as part of the docker build process. It is kYc0o's hackathon_suit_2018
branch. The keys.h target in examples/suit_updater/Makefile also needs to be
set to the upload location of the public key in the docker container, which is
as of the time of writing /app2/ota-resources/pubkeys/pub.key.

The manifest is being generated, and signed in the browser, however the
verification of the manifest on the node needs to be tested and debugged. I.e.
the next stage of development is end-to-end integration and testing.

Features that can be added are:
- support to build any application as "ota-ready", i.e. with an endpoint,
  flashing functionality, etc. With different app pages
- Demonstration/debugging of revocation of public keys by re-uploading a new
  one
- re-write keygen as a double-click application, possibly with some
  randomization
- make the applications boot slot agnostic, i.e. so that the image is
  automatically generated for whichever is the vacant slot
- implement a device preparation app which automatically and securely notifies
  the server of the device's address, so that the device appears on the "app"
  pages, perhaps as an icon. I.e. device auto-discovery
