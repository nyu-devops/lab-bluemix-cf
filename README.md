# Bluemix Python Web application
This repository is part of lab for the *NYU DevOps* class for Spring 2017, [CSCI-GA.3033-013](http://cs.nyu.edu/courses/spring17/CSCI-GA.3033-013/)

The sample code is using [Flask microframework](http://flask.pocoo.org/) and is intented to test the Python support on [IBM's Bluemix](https://bluemix.net/) environment which is based on Cloud Foundry. It also uses [Redis](https://redis.io) as a database for storing JSON objects.

IBM Bluemix contains the Python buildpack from [Cloud Foundry](https://github.com/cloudfoundry/python-buildpack) and so will be auto-detected as long as a requirements.txt or a setup.py is located in the root of your application.

Follow the steps below to get the lab code and see how to deploy manually.

## Prerequisite Installation using Vagrant
The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/)

## Get the lab code
From a terminal navigate to a location where you want this application code to be downloaded to and issue:
```bash
    $ git clone https://github.com/nyu-devops/lab-bluemix-cf.git
    $ cd lab-bluemix-cf
    $ vagrant up
    $ vagrant ssh
    $ cd /vagrant
```
This will place you into an Ubuntu VM all set to run the code.

You can run the tests to make sure that the code works with the following command:

    $ nosetests -v --rednose --nologcapture

You can run the code to test it out in your browser with the following command:

    $ python server.py

You should be able to see it at: http://localhost:5000/

When you are done, you can use `Ctrl+C` to stop the server and then exit and shut down the vm with:

## Deploy to Bluemix manually
Before you can deploy this applicaiton to Bluemix you MUST edit the `manifest.yml` file and change the name of the application to something unique. I recommend changng the last two letters to your initials as a start. If that doesnt work, start adding numbers to make it unique.

Then from a terminal login into Bluemix and set the api endpoint to the Bluemix region you wish to deploy to:
```script
cf login -a api.ng.bluemix.net
```
The login will ask you for you `email`(username) and `password`, plus the `organisation` and `space` if there is more than one to choose from.

From the root directory of the application code execute the following to deploy the application to Bluemix. (By default the `route` (application URL) will be based on your application name so make sure your application name is unique or use the -n option on the cf push command to define your hostname)
```script
cf push <YOUR_APP_NAME> -m 64M
```
to deploy when you don't have a requirements.txt or setup.py then use:
```script
cf push <YOUR_APP_NAME> -m 64M -b https://github.com/cloudfoundry/python-buildpack
```
to deploy with a different hostname to the app name:
```script
cf push <YOUR_APP_NAME> -m 64M -n <YOUR_HOST_NAME>
```

## View App
Once the application is deployed and started open a web browser and point to the application route defined at the end of the `cf push` command i.e. http://lab-bluemix-xx.mybluemix.net/. This will execute the code under the `/` app route defined in the `server.py` file. Navigate to `/pets` to see a list of pets returned as JSON objects.

## Structure of application
**Procfile** - Contains the command to run when you application starts on Bluemix. It is represented in the form `web: <command>` where `<command>` in this sample case is to run the `py` command and passing in the the `server.py` script.

**requirements.txt** - Contains the external python packages that are required by the application. These will be downloaded from the [python package index](https://pypi.python.org/pypi/) and installed via the python package installer (pip) during the buildpack's compile stage when you execute the cf push command. In this sample case we wish to download the [Flask package](https://pypi.python.org/pypi/Flask) at version 0.12 and [Redis package](https://pypi.python.org/pypi/Redis) at version greater than or equal to 2.10

**runtime.txt** - Controls which python runtime to use. In this case we want to use 2.7.9.

**README.md** - this readme.

**manifest.yml** - Controls how the app will be deployed in Bluemix and specifies memory and other services like Redis that are needed to be bound to it.

**server.py** - the python application script. This is implemented as a simple [Flask](http://flask.pocoo.org/) application. The routes are defined in the application using the @app.route() calls. This application has a `/` route and a `/pets` route defined. The application deployed to Bluemix needs to listen to the port defined by the VCAP_APP_PORT environment variable as seen here:
```python
port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
```

This is the port given to your application so that http requests can be routed to it. If the property is not defined then it falls back to port 5000 allowing you to run this sample application locally.
