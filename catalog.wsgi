#import system functions
import sys
"""
Catalog.wsgi - Runs the catalog application
"""
#add the path to the app for importing
sys.path.insert(0, '/var/www/catalog/app')
#import the app as application. WSGI uses this to handle the requests.
from application import app as application
