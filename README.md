# IBM Cloud Python Web application

[![Build Status](https://github.com/nyu-devops/lab-bluemix-cf/actions/workflows/workflow.yml/badge.svg)](https://github.com/nyu-devops/lab-bluemix-cf/actions)

[![codecov](https://codecov.io/gh/nyu-devops/lab-bluemix-cf/branch/master/graph/badge.svg?token=dCToV9ysTt)](https://codecov.io/gh/nyu-devops/lab-bluemix-cf)

This repository is part of lab for the *NYU DevOps* class, [CSCI-GA.2820-​001 ](http://cs.nyu.edu/courses/spring17/CSCI-GA.3033-013/)

The sample code is using [Flask micro-framework](http://flask.pocoo.org/) with [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/index.html) and is intended to test the Python support on [IBM Cloud](https://cloud.ibm.com/) environment which is based on Cloud Foundry. It also uses [Cloudant](https://www.ibm.com/cloud/cloudant) as a database for storing JSON objects.

IBM Cloud contains the Python buildpack from [Cloud Foundry](https://github.com/cloudfoundry/python-buildpack) and so will be auto-detected as long as a `requirements.txt` or a `setup.py` is located in the root of your application.

Follow the steps below to get the lab code and see how to deploy manually.

## Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/)

## Get the lab code

From a terminal navigate to a location where you want this application code to be downloaded to and issue:

```bash
git clone https://github.com/nyu-devops/lab-bluemix-cf.git
cd lab-bluemix-cf
vagrant up
vagrant ssh
cd /vagrant
```

This will place you into an Ubuntu VM all set to run the code.

## Prerequisite Installation using Visual Studio Code and Docker

You can also develop in Docker containers using VSCode. This project contains a `.devcontainer` folder that will set up a Docker environment in VSCode for you. You will need the following:

- Docker Desktop for [Mac](https://docs.docker.com/docker-for-mac/install/) or [Windows](https://docs.docker.com/docker-for-windows/install/)
- Microsoft Visual Studio Code ([VSCode](https://code.visualstudio.com/download))
- [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VSCode Extension

It is a good idea to add VSCode to your path so that you can invoke it from the command line. To do this, open VSCode and type `Shift+Command+P` on Mac or `Shift+Ctrl+P` on Windows to open the command palette and then search for "shell" and select the option **Shell Command: Install 'code' command in Path**. This will install VSCode in your path.

Then you can start your development environment up with:

```bash
git clone https://github.com/nyu-devops/lab-bluemix-cf.git
cd lab-bluemix-cf
code .
```

The first time it will build the Docker image but after that it will just create a container and place you inside of it in your `/app` folder which actually contains the repo shared from your computer. It will also install all of the VSCode extensions needed for Python development.

If it does not automatically pronot you to open the project in a container, you can select the green icon at the bottom left of your VSCode UI and select: **Remote Containers: Reopen in Container**.

## Run the tests

Before you modify any code you should always run teh test suit to be sure that nothing is broken bedfore you start.

You can run the tests to make sure that the code works with the following command:

```bash
nosetests
```

### Run the Service

In order to run the service you will need to have some environment variables set (in true 12-factor fashion). This reo has an example called `dot-env-example` which you can simply use. Copy it to a file called `.env` with this command:

```bash
cp dot-env-example .env
```

You only need to do this once. Now every time you run the application, it will pick up those environment variatbels whcih tell it where to find the database and how to login.

_Note:_ If you are developing using VSCode and devcontainers, you will need to edit the `.env` file to change the `COUCHDB_HOST` environment variable from `localhost` to `couchdb` because your instance of CouchDB will be running in a  container with that name. If you are using a Vagrant VM you can leave it as `localhost`.

You can run the code to test it out in your browser with the following command:

```bash
honcho start
```

You should be able to see it at: http://localhost:8080/

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

## Deploy to IBM Cloud manually

Before you can deploy this application to IBM Cloud you MUST edit the `manifest.yml` file and change the name of the application to something unique. I recommend changing the last two letters to your initials as a start. If that doesn't work, start adding numbers to make it unique.

Then from a terminal login into IBM Cloud and set the api endpoint to the IBM Cloud region you wish to deploy to:

```bash
ic cf login -a https://cloud.ibm.com
```

The login will ask you for you `email`(username) and `password`, plus the `organization` and `space` if there is more than one to choose from.

From the root directory of the application code execute the following to deploy the application to IBM Cloud. (By default the `route` (application URL) will be based on your application name so make sure your application name is unique or use the -n option on the cf push command to define your hostname)

```bash
ic cf push <YOUR_APP_NAME> -m 64M
```

to deploy when you don't have a `requirements.txt` or `setup.py` then use:

```bash
ic cf push <YOUR_APP_NAME> -m 64M -b https://github.com/cloudfoundry/python-buildpack
```

to deploy with a different hostname to the app name:

```bash
ic cf push <YOUR_APP_NAME> -m 64M -n <YOUR_HOST_NAME>
```

## View App

Once the application is deployed and started open a web browser and point to the application route defined at the end of the `cf push` command i.e. http://lab-bluemix-xx.us-south.cf.appdomain.cloud/. This will execute the code under the `/` app route defined in the `resources.py` file. Navigate to `/pets` to see a list of pets returned as JSON objects.

## Structure of application

**Procfile** - Contains the command to run when you application starts on IBM Cloud. It is represented in the form `web: <command>` where `<command>` in this sample case is to run the `gunicorn` command and passing in the location of the Flask app as `service:app`.

**requirements.txt** - Contains the external python packages that are required by the application. These will be downloaded from the [python package index](https://pypi.python.org/pypi/) and installed via the python package installer (pip) during the buildpack's compile stage when you execute the cf push command. In this sample case we wish to download the [Flask package](https://pypi.python.org/pypi/Flask) at version 1.0.2 and [Cloudant package](https://pypi.python.org/pypi/Cloudant) at version 2.9.0.

**runtime.txt** - Controls which python runtime to use. In this case we want to use Python 3.9.

**README.md** - this readme.

**manifest.yml** - Controls how the app will be deployed in IBM Cloud and specifies memory and other services like Redis that are needed to be bound to it.

**service** - the python package that contains fthe applciation. This is implemented as a simple Flask-RESTX application. The routes are defined in the application using the `api.add_resource()` calls. This application has a `/` route and a `/pets` route defined.

The application deployed to IBM Cloud needs to listen to the port defined by the VCAP_APP_PORT environment variable as seen here:

```python
port = os.getenv('VCAP_APP_PORT', '8080')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
```

This is the port given to your application so that http requests can be routed to it. If the property is not defined then it falls back to port `5000` which is the default port for Flask allowing you to run this sample application locally.
