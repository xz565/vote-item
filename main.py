#!/usr/bin/env python

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

from models import Account
from models import Category
from models import Item

from vote_handler import VoteHandler
from manage_handler import ManageHandler


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            self.checkUser(user)

            template_values = {
                'nickname': user.nickname(),
                'logout_url': users.create_logout_url("/")
            }
            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            greeting = ("<a href=\"%s\">Sign in or register</a>." %users.create_login_url("/"))
            self.response.out.write("""
                <html>
                    <body>%s</body>
                </html>
                """ % greeting)


    def checkUser(self, user):
        accounts = Account.all()
        user_ids = []
        for acc in accounts:
            user_ids.append(acc.user_id)

        uid = user.nickname()
        if uid not in user_ids:
            account = Account(key_name=uid, user_id=uid)
            account.put()


class OptionHandler(webapp2.RequestHandler):
    def get(self):
        option = self.request.get("option")

        if option == "manage":
            self.manage_page()

        elif option == "vote":
            self.choose_account_page()


    def manage_page(self):
        currt_user = users.get_current_user()
        account_key = db.Key.from_path('Account', currt_user.nickname())
        categories = Category.all()
        categories.ancestor(account_key)

        items = Item.all()

        template_values = {
            'categories': categories,
            'items': items,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.out.write(template.render(path, template_values))


    def choose_account_page(self):
        accounts = Account.all()
        template_values = {
            'accounts': accounts,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'choose_account.html')
        self.response.out.write(template.render(path, template_values))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/option', OptionHandler),
    ('/manage', ManageHandler),
    ('/vote', VoteHandler),
    #('/serve/([^/]+)?', ServeHandler)
], debug=True)

