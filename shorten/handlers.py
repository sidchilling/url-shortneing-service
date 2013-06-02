import os
import urllib
import logging
import json
import hashlib

import jinja2
import webapp2

from google.appengine.api import users
from services import services
from services import httpagentparser

JINJA_ENVIRONMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape']
	)

class MainPage(webapp2.RequestHandler):
    
    def get(self):
	user = users.get_current_user()
	if user:
	    template = JINJA_ENVIRONMENT.get_template('html/index.html')
	    self.response.write(template.render())
	else:
	    self.redirect(users.create_login_url(self.request.uri))
    
class Redirect(webapp2.RequestHandler):
    def get(self, link_id):
	try:
	    try:
		ua_info = httpagentparser.detect(self.request.headers['User-Agent'])
		services.insert_visit(link_id = link_id, ua_info = ua_info)
	    except:
		logging.exception('exception while parsing and insering user agent')
	    link_id = link_id.strip()
	    template_values = {
		    'original_url' : services.get_original_url(link_id = int(link_id))
		    }
	    template = JINJA_ENVIRONMENT.get_template('/html/redirect.html')
	    self.response.write(template.render(template_values))
	except:
	    self.response.write('Something went wrong. Very sorry')

class GetShortURL(webapp2.RequestHandler):
    def _make_error_response(self, reason):
	return {
		'error' : True,
		'reason' : reason
		}

    def post(self):
	response = {}
	if not self.request.get('url', None):
	    response = self._make_error_response(reason = 'URL not given')
	user = users.get_current_user()
	if not user:
	    response = self._make_error_response(reason = 'User not authorized')
	else:
	    if not services.check_url(url = self.request.get('url')):
		response = self._make_error_response(reason = 'The URL is not reachable')
	    else:
		try:
		    link_id = services.db_insert_link(user = user,
			    url = self.request.get('url'))
		    from config.config import Config
		    response = {
			    'success' : True,
			    'data' : {
				'short_url' : '%s/r/%s' %(Config.SERVER_PREFIX, link_id),
				}
			    }
		except Exception as e:
		    logging.exception('exception: %s' %(e))
		    response = self._make_error_response(reason = 'Unexpected error')
	self.response.headers['Content-Type'] = 'application/json'
	self.response.write(json.dumps(response))

class Analytics(webapp2.RequestHandler):
    def get(self):
	user = users.get_current_user()
	if not user:
	    self.redirect(users.create_login_url(self.request.uri))
	else:
	    (data, os_browser_list) = services.get_analytics(user = user)
	    template_values = {
		    'data' : data,
		    'os_browser_list' : os_browser_list
		    }
	    template = JINJA_ENVIRONMENT.get_template('html/analytics.html')
	    self.response.write(template.render(template_values))

class UserDetails(webapp2.RequestHandler):
    def post(self):
	response = {}
	user = users.get_current_user()
	if not user:
	    respone = {
		    'error' : True,
		    'reason' : 'unauthenticated'
		    }
	else:
	    data = {
		    'nickname' : user.nickname(),
		    'email' : user.email(),
		    'user_id' : user.user_id(),
		    'federated_identity' : user.federated_identity(),
		    'federated_provider' : user.federated_provider()
		    }
	    response = {
		    'success' : True,
		    'data' : data
		    }
	self.response.headers['Content-Type'] = 'application/json'
	self.response.write(json.dumps(response))
