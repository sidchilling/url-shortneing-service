from google.appengine.api import urlfetch
from models import models
from google.appengine.ext import db
import logging
import json

def check_url(url):
    # checks whether the given URL is reachable or not
    try:
	result = urlfetch.fetch(url)
	if result.status_code == 200:
	    return True
	return False
    except Exception as e:
	logging.exception('exception while checking url: %s' %(e))
	return False

def _check_link(user, url):
    # check whether a link already exists
    q = db.GqlQuery('SELECT * FROM Link WHERE user_id = :1 AND link = :2', user.user_id(),
	    url)
    for link in q.run(limit = 5):
	return (True, link.key().id())
    return (False, None)

def db_insert_link(user, url):
    # Inserts a new link in the database
    (exists, link_id) = _check_link(user = user, url = url)
    if not exists:
	link = models.Link(user_id = user.user_id(), link = url)
	link.put()
	link_id = link.key().id()
    return link_id

def insert_visit(link_id, ua_info):
    # Logs a visit - either makes a new entry or increments the count
    q = db.GqlQuery('SELECT * FROM Visit WHERE link_id = :1 AND os = :2 AND \
	    browser = :3', link_id, ua_info.get('os', {}).get('name', {}),
	    ua_info.get('browser', {}).get('name', ''))
    found = False
    id = None
    count = 1
    for v in q.run(limit = 1):
	id = v.key().id()
	found = True
	count = v.count + 1
    if found:
	visit = models.Visit.get_by_id(int(id))
	visit.delete()
    visit = models.Visit(link_id = link_id, os = (ua_info.get('os', {}).get('name', {})).strip(),
	    browser = (ua_info.get('browser', {}).get('name', '')).strip(),
	    count = count)
    visit.put()

def get_original_url(link_id):
    # Gets the original URL of a link given the link id
    link = models.Link.get_by_id(link_id)
    if not link:
	return None
    return link.link

def get_analytics(user):
    # Get the analytics given a user
    # Get all the links first
    res = {} # return
    q = db.GqlQuery('SELECT * FROM Link WHERE user_id = :1', user.user_id())
    for link in q.run(limit = 1000):
	# Assuming not more than 1000 links for a user
	res[link.key().id()] = {
		'original_url' : link.link,
		'data' : {}
		}
    
    os_browser_list = [] # A list containing the name of os and browser
    # Do for all the link ids
    for link_id in res.keys():
	link_res = {}
	visits_query = db.GqlQuery('SELECT * FROM Visit WHERE link_id = :1', '%s' %(link_id))
	for visit in visits_query.run(limit = 1000):
	    # assuming there are not more than 1000 useragents for a link id
	    os_browser_name = '%s (%s)' %(visit.browser, visit.os)
	    if os_browser_name not in os_browser_list:
		os_browser_list.append(os_browser_name)
	    
	    link_res[os_browser_name] = visit.count
	    res[link_id]['data'] = link_res
    return (res, os_browser_list)


