import os
import sys
sys.path.insert(0, '/var/www/entweb')
os.environ['ENTWEB_SETTINGS'] = '/var/www/entweb/etc/entweb.cfg'

from entweb import app as application

