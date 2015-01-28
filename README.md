# EntWeb

EntWeb is an index page for GitHub Enterprise that resembles the classic GitWeb main page.
Why when GitHub is so awesome?  It's a bit hard to search for projects at a large company.
This may also help herd stubborn devlopers away from old services (I'm one of them).

### Requirements

EntWeb was built upon a bunch of open source tech

* [Github API] - Github. duh. Go get an account, register for an app id
* [Python] - The app is written in python
* [Flask] - A small neat python web development framework
* [Flask-Cache] - Cache extension for Flask
* [requests] - web request library for python
* [mod_wsgi] - Allows you to host python apps in Apache

### Installation Instructions

```sh
# get requirments
sudo apt-get install libapache2-mod-wsgi python-pip apache2 git
sudo pip install requests Flask

# download entweb into the web folder
sudo mkdir -p /var/www
cd /var/www
sudo git clone git@github.com:marek/entweb.git
sudo chown root:www-data entweb

# configure entweb as the site
sudo ln -s sudo ln -s /var/www/entweb/etc/entweb.conf  /etc/apache2/sites-available/entweb.conf
sudo a2ensite entweb
sudo a2dissite defualt # Run if you want to disable the default index page
```


Go to github.com and register an application. Set the callback url to `http://<yourhost>/access`

Next edit your `/var/www/entweb/etc/entweb.cfg`
```sh
APP_CLIENTID = '<app client id>'
APP_SECRETID = '<app secret id>'
SECRET_KEY = '<random secret key for this deployment>'

GITHUB_API_URL = 'https://api.github.com'
GITHUB_OAUTH_URL = 'https://github.com'

DEBUG = True
TESTING = True
```

Finally restart apache!

```sh
sudo service restart apache2
```

** Note: If you don't install to `/var/www/entweb` make sure to update the paths in `/var/www/entweb/entweb.wsgi` as well



