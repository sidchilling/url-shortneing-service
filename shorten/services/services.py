from google.appengine.api import urlfetch
from models import models
from google.appengine.ext import db
import logging
import json

def check_url(url):
    try:
	result = urlfetch.fetch(url)
	if result.status_code == 200:
	    return True
	return False
    except Exception as e:
	logging.exception('exception while checking url: %s' %(e))
	return False

def _check_link(user, url):
    q = db.GqlQuery('SELECT * FROM Link WHERE user_id = :1 AND link = :2', user.user_id(),
	    url)
    for link in q.run(limit = 5):
	return (True, link.key().id())
    return (False, None)

def db_insert_link(user, url):
    (exists, link_id) = _check_link(user = user, url = url)
    if not exists:
	link = models.Link(user_id = user.user_id(), link = url)
	link.put()
	link_id = link.key().id()
    return link_id

def insert_visit(link_id, ua_info):
    visit = models.Visit(link_id = link_id, os = ua_info.get('os', {}).get('name', ''),
	    browser = ua_info.get('browser', {}).get('name', ''),
	    ua_string = json.dumps(ua_info))
    visit.put()

def get_original_url(link_id):
    link = models.Link.get_by_id(link_id)
    if not link:
	return None
    return link.link
