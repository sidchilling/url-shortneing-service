import datetime
from google.appengine.ext import db

class Link(db.Model):
    user_id = db.StringProperty(required = True, indexed = True)
    link = db.StringProperty(required = True, indexed = True)
    date = db.DateTimeProperty(auto_now_add = True)

class Visit(db.Model):
    # Not keeping just counts as we can store the total visit history
    # to find interesting analytics over time
    link_id = db.StringProperty(required = True, indexed = True)
    os = db.StringProperty(required = True, indexed = True)
    browser = db.StringProperty(required = True, indexed = True)
    ua_string = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add = True)
