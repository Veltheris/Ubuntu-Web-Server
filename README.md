#Linux Web Server
Configuration for a webserver from a base Ubunty 14 "Trusty".

Table of Contents
- Setup/Requirements
- Connection
- Application Installs
- Configuration
- Changelog
- Comments


##Setup / Requirements
These are instructions for the applications and configurations to host a Python WSGI application on a Ubuntu 14 "Trusty" server. For this project, the setup was done on a virtual machine provided by Udacity.
The Python application to be set up is a copy of my Item Catalog Application, modified to be used without vagrant. A partial version is available [here](https://github.com/Veltheris/Item-Catalog-Base).
The only requirements to get this working on a new machine would be a Ubunty 14 "Trusty" (Other versions may work) os and an internet connection.

##Connection
The server can be accessed directly through SSH, or just the website via HTTP.
SSH Connection is `grader@52.27.107.193` on port `2200`. Connecting to it requires SSH and a RSA private key. Key not included with this README for security reasons.
The website is at [http://ec2-52-27-107-193.us-west-2.compute.amazonaws.com/](http://ec2-52-27-107-193.us-west-2.compute.amazonaws.com/), and works fully. [http://52.27.107.193/](http://52.27.107.193/) also works.

## Application Installs
The webserver needs applications to be able to host the website, and while some are included, most must be installed. As a branch of Debian, Ubuntu includes the Apt package manager. Apt was use to install the following programs. Note that many triggered installation of other apts as prerequisites.

###Apt-Get
- apache2: (Required) Apache Web Server. Installed by default.
- cron: (Required) Cron Command Scheduler. Installed by default.
- git: (Optional) GitHub program. Used to transfer a copy of the application to the server.
- libapache2-mod-python: (Required) Apache2 support for Python.
- libapache2-mod-wsgi: (Required) Apache support for Python's Web Service Gateway Interface.
- ntp: (Optional) Time syncronization service.
- postgresql: (Required) PostgreSQL Database. Installed by default.
- postgresql-server-dev-9.3: (Required) Development Server and Utilites. Required for the Python connection to work.
- python: (Required)
- python-dev: (Required)
- python-pip: (Optional) PyPA Python Module Installer.
- ufw: (Required) Uncomplicated Firewall. Installed by default.
- unattended-upgrades: (Optional) Script for APT to run updates on it's own. Installed by default.

Once those it was installed, pip was used to install some modules for python. All are required for the application to function.

###PiP
- sqlalchemy: SQLAlchemy Object-Relational Mapper. Used to allow streamlined use of the database.
- flask: Flask Web Framework. Python module that serves web sites.
- flask-sqlalchemy: Bridge for Flask and SQLAlchemy. Controls SQLAlchemy to make it better for use in a threaded website.
- flask-seasurf: Flask Cross Site Request Forgery (CSRF) prevention. Adds and checks for secure tokens in POST requests.
- psycopg2: Psycopg Python PostgreSQL bridge. Allows python to connect and use PostgreSQL databases.
- oauth2client: Google Oauth2Client. Used for logging in to the website with Google+.

##Configuration
Once these applications are installed, it's time to change some configurations to get them to work together.

###Account and Security Steps
The first thing that should be done is setting up the accounts, sudoers, ssh, and the firewall. While a good idea for security, it is essential as a mistake on one of those may lock out access to the server completely, requireing a reinstall.
- Added the accounts student, grader, and catalog.
- Opened `/etc/sudoers.d`
  - Added student and grader files to allow sudo. They have full sudo permissions, without password entry.
- Opened `/etc/ssh/sshd_config`
  - Changed SSH to port 2200, disabled password authentication and root login.
- Configured UFW to default to deny incoming and allow outgoing. `ufw default deny incoming` `ufw default allow outgoing`
- Configured UFW to allow 123 and 80/tcp. SSH was set to `limit 2200/tcp`. This makes repeated unsuccessful logins result in bans. `ufw allow 80/tcp` `ufw allow 123` `ufw limit 2200/tcp`
- Restarted and Enabled UFW, and Restarted SSH.

###Updates and Cron
One of the easiest ways to give a web server some security is to simply keep it updated. `Apt-Get Update` and `Upgrade` were run to bring the server up to date, but a cron script can ensure it stays updated on it's own.
While looking into cron to see how to best implement this, I noticed that apt has it's own settings on `cron.daily`. These include a number of settings for a script called unattended upgrades, installed by default on ubuntu.
I created a file to configure the settings and placed it in `/etc/apt/apt.conf.d/02periodic` The full file I created is in this repository.
I also ran `ntpd` to start the daemon to keep the clock synchronized.

###Apache Configuration
While the apache extensions have taught it how to serve WSGI applications, it needs to have an application to server. I disabled the default website with `a2dissite 000-default`. And added the file `catalogserver.conf` to `/etc/apache2/sites-available`. This file designates a WSGI application, to be served at `/var/www/catalog/app/catalog.wsgi`, set up below. The running of the WSGI application is delegated to a daemon called catalogserver, running as the catalog user.

###Website Placement and Setup
Apache2 now knows what to server, so all that's left is to place and setup the website. I navigated to `var/www` and used `git clone https://github.com/Veltheris/Item-Catalog-Base`. This created a full copy of the catalog project in the directory. I used `mv` to rename the folder to catalog, and the actually application to `app`.
To actually serve the website, the catalogserver daemon will need some access to these files. I used `chgrp` to put these files in the catalog group (of which the user catalog is the sole member). `chmod` made sure that while root had full access to the files, the catalog group could only read and execute them.
To allow the database to work, it needs to exist, and the catalogserver daemon needs access to it as well. Inside `sudo -u postgres psql` , I used `create user catalog;` to create the catalog user in postgresql. Thanks to the way PostgreSQL handles authentication by default, the catalog system user can log on as the catalog postgreSQL user. I used `sudo -u postgres createdb catalog` to create a database of that name.

###Starting it up
After checking the paths to make sure they work, and modifing the `client_secrets.json` file to account for the new domain (And changing it on console.developers.google.com), The website should be ready.
It's time to turn it on. I ran `sudo a2ensite catalogserver` to enable the webserver, and ran `sudo service apache2 reload` to restart apache2 with the new site.

That is how I configured the website. It should be secure, auto-updating, and running the item catalog application.

##Changelog
###Version 1.0
- First Submitted Version.

###Comments
This was a cool project. I had set up a raspberry pi as a web server, but this is a lot more thorough.
Interestingly, I never noticed before that ssh under Ubuntu seems to have legacy connections? While changing SSH settings changed it for all future SSH connections, it never disconnected any in use connections on the old port. UFW seemd to do the same thing.