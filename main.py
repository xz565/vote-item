#!/usr/bin/env python

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
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" \
                            %(user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." \
                            %users.create_login_url("/"))

        self.response.out.write("<html><body>%s</body></html>" % greeting)


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
