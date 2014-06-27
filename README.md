sportsfronter-heroku-test
========================

Overview
--------

This repo is created just to test keeping a synced Heroku and Github repo.

This repo contains both a webapp (sportsfronter api and the web frontend) and Android and iOS apps. 

The backend maintains state, sends notification etc. The frontend applications are nearly
the same, one accessible via a browser (f.ex. from a PC), the other two from Android or iOS
devices. The Android and iOS apps use Cordova, i.e. it is mostly HTML and JS with a little
native code to integrate it into the system and to be able to receive push messages.


Application structure
---------------------

* `webapp` - the backend API and web frontend
* `android` - android app that wraps the web client via Cordova and handles push messages
* `ios` - the iOS app, similar to the Android app


Setting up the Development environment
--------------------------------------

Vagrant is a command-line utility for creating virtual machines (VM) and installing and configuring software on them. 
It starts the VM in a headless mode, shares folders (f.ex. this one as `/vagrant`), forwards ports to the host machine, 
and runs a provisioner such as Puppet or shell to install and configure stuff on the machine.

In our case, it will provide a fully functional development environment 
(backend api and web client - ios and android apps use their own test environments).


### Quick start:

1. Install latest [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](http://downloads.vagrantup.com/).
2. Run `vagrant plugin install vagrant-vbguest` to install the [vagrant-vbguest](https://github.com/dotless-de/vagrant-vbguest) plugin to automatically update the guest additions as needed.
3. Run `vagrant up` to create and start the VM which will run all services needed.

Upon start, Vagrant will install all the dependencies, initialize the webapp
(creating the admin user `vagrant` having the password `vagrant`) and start
it on port 5000, which is also forwarded to the host machine's port 5000.

The webapp should thus be accessible from http://localhost:5000/ and the admin site on http://localhost:5000/admin/.


When Developing…
-----------------

To access the dev environment, go to the project root folder and run `vagrant ssh`.

**Important:** when you make changes to the backend code, run `sudo restart sportsfronter-backend` inside of the Vagrant.

Backend Log: `sudo less /var/log/upstart/sportsfronter-backend.log` (inside vagrant)


Key commands (run from this directory):

* `vagrant up` to start (and, upon first use, create) the VM
* `vagrant ssh` to ssh into the VM (with full access to sudo)
* `vagrant halt` to stop the VM
* (`vagrant destroy` to stop and completely remove the VM; re-create with `up`)


To reload the backend service whenever there is changes in the python files run the following command from the vagrant box.
    
    filewatcher -r /vagrant/ -n *.py "sudo restart sportsfronter-backend"

Possible error: "Vagrant error : Failed to mount folders in Linux guest". If you encounter this error, try `vagrant ssh`, followed by:
`sudo ln -s /opt/VBoxGuestAdditions-4.3.10/lib/VBoxGuestAdditions /usr/lib/VBoxGuestAdditions`
See http://stackoverflow.com/questions/22717428/vagrant-error-failed-to-mount-folders-in-linux-guest and/or https://github.com/mitchellh/vagrant/issues/3341.



### Changes to Sass files (CSS preprocessor)

**TODO**: This should also be available in the vagrant box.

1\. Install Sass

    gem install sass

2\. Navigate into the prosject's static-folder

    cd sportsfronter/static/webapp

3\. Run Sass, and watch for changes

    sass --watch scss/style.scss:css/style.css --style compressed


Staging
-------

The staging environment is located at sportsfronter.app.iterate.no

To deploy to staging, run `deploy.sh`


Production
----------

The production environment is [sportsfronter.iterate.no](http://sportsfronter.iterate.no).

You need sudo on the server and access to the user `iterate-www-sportsfronter` (ask the guys at ops@iterate.no).

When access is obtained, basically just get the latest changes from the github repo in the folder
`/srv/sporsfronter.iterate.no/checkout/sommer2013-sportsfronter/` to deploy the updates.

After deploying, you should restart the service:

	sudo service apache2 graceful

### Log

The backend log for the production environment can be found at `/tmp/sportsfronter.log`


### Crontab

A cron-job that sends messages is running on the server. Access it by logging in to the user `iterate-www-sportsfronter`(see Deployment) and opening the crontab for this user: `crontab -e`


### Database Admin

Admin pages: `https://sportsfronter.iterate.no/admin`

Admin Username: `admin`

Admin Password: `iterate123`


Production/Staging - Heroku
---------------------------

Test/staging instance: http://sportsfronter-heroku-test.herokuapp.com/


Analytics
---------
Sportsfonter uses Google Analytics. Account name: Sportsfronter. To get access to the account, ask one of the devs.


