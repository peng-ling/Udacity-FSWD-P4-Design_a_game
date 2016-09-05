# Udacity-FSWD-P4-Design_a_game

[spec](https://review.udacity.com/#!/rubrics/144/view)

[To run your app, be sure to deploy the 'Shield Trick' which is allowing scripts to run on your browser by clicking on the shield icon on the right side of your URL bar. You can read more about it in this forum discussion] (https://discussions.udacity.com/t/warning-when-accessing-apis-explorer-from-local-host-version-of-hello-endpoints/26056?_ga=1.197288364.2083839808.1448871235)

[Also, this discussion on running the API explorer will come in handy later in the course]
(https://discussions.udacity.com/t/exploring-conferenceapi-the-api-you-are-exploring-is-hosted-over-http-which-can-cause-problems/47383?_ga=1.197288364.2083839808.1448871235)


## Creating a new project

[google developer console]
(https://console.developers.google.com/)

1. Go here: https://console.developers.google.com
2. Select Create project
3. Click Edit to view the Project ID field
4. Choose a unique project id
5. Give your project a name (doesn't have to be unique)
6. Click Create

## Coding environment setup

[SDK - download and install Google App Engine SDK for Python](https://cloud.google.com/appengine/downloads)

Running Google App Engine on Mac OS
Unfortunately Google no longer supports the GoogleAppengineLauncher program that Karl mentions in this video. You follow use the instructions below for Linux, or you can download the deprecated GoogleAppengineLauncher installer from the "Supporting Materials" list below. Warning: Use the GoogleAppengineLauncher program at your own peril! As Google no longer supports the tool it may stop working in the future.

Running Google App Engine on Linux
To run the Development Web Server locally, run:

dev_appserver.py myapp
Where myapp is the name you want your app to have.

To upload your code to Google App Engine, run:

appcfg.py update helloworld/
Where helloworld/ is the directory you're running your web app from.

Further help is available [here](https://developers.google.com/appengine/docs/python/tools/devserver) and [here](https://developers.google.com/appengine/docs/python/gettingstartedpython27/uploading)

## Course Repository

[The GitHub repository can be found here](https://github.com/udacity/ud858)

## deploy the app

console, within the appfolder:

appcfg.py -A devscalappswithpython -V v1 update ./


## Accessing the deployed app:

[project-id].appspot.com
e.g. devscalappswithpython.appspot.com

## Decorators

More on decorators:

[1](https://realpython.com/blog/python/primer-on-python-decorators/)
[2](http://www.learnpython.org/en/Decorators)
[3](https://www.python.org/dev/peps/pep-0318/)
[4](http://www.jeffknupp.com/blog/2013/11/29/improve-your-python-decorators-explained/)

## Google Protocol RPC Library Overview

[The Google Protocol RPC library is a framework for implementing HTTP-based remote procedure call (RPC) services. An RPC service is a collection of message types and remote methods that provide a structured way for external applications to interact with web applications. Because you can define messages and services in the Python programming language, it's easy to develop Protocol RPC services, test those services, and scale them on App Engine.](https://cloud.google.com/appengine/docs/python/tools/protorpc/)

## api explorer

http://localhost:8080/_ah/api/explorer

## Chrome needs to be started in a special way to use api explorer

How do I use Explorer with a local HTTP API?

If you use Google Cloud Endpoints, and you are running your Endpoint in a development server, your browser may complain about mixed content. Explorer is loaded over HTTPS, but your API (when running locally) is hosted on HTTP.

To resolve this, using Chrome, you must start a Chrome session with special flags as follows:

[path-to-Chrome] --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:port
or a more concrete example:

 /usr/bin/google-chrome-stable --user-data-dir=test --unsafely-treat-insecure-origin-as-secure=http://localhost:8080
You should only do this for local testing purposes, in which case you can ignore the warning banner displayed in the browser.

## Google Hello World example

[It is a Python "Hello World" skeleton application for Google App Engine using Google Cloud Endpoints, available from Google Cloud GitHub repository](https://github.com/GoogleCloudPlatform/appengine-endpoints-helloendpoints-python)
