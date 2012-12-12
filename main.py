#!/usr/bin/env python

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import webapp2


class UserPrefs(db.Model):
    userid = db.StringProperty()


class Category(db.Model):
    cat_name = db.StringProperty()
    user_name = db.StringProperty()


class Vote(db.Model):
    owner = db.StringProperty()
    category = db.StringProperty()
    win = db.StringProperty()
    lose = db.StringProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            template_values = {
                'nickname': user.nickname(),
                'logout_url': users.create_logout_url("/")
            }
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." \
                            %users.create_login_url("/"))
            self.response.out.write("<html><body>%s</body></html>" % greeting)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
