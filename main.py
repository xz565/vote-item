#!/usr/bin/env python

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import webapp2


class Account(db.Model):
    user_id = db.StringProperty()


class Category(db.Model):
    cat_name = db.StringProperty()
    items = db.StringListProperty()

class Vote(db.Model):
    owner = db.StringProperty()
    category = db.StringProperty()
    win = db.StringProperty()
    lose = db.StringProperty()


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
            greeting = ("<a href=\"%s\">Sign in or register</a>." \
                            %users.create_login_url("/"))
            self.response.out.write("<html><body>%s</body></html>" % greeting)

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
        new_cat = self.request.get("new_cat")
        new_item = self.request.get("new_item")

        if option == 'manage':
            self.manage_page()

        elif option == 'vote':
            self.account_page()

        if new_cat:
            self.add_category(new_cat)
            self.manage_page()

        if new_item:
            self.add_item(new_item)
            self.manage_page()


    def add_item(self, new_item):
        currt_user = users.get_current_user()
        cat_name = self.request.get("category")
        cat_key = db.Key.from_path('Account', currt_user.nickname(), 'Category', cat_name)

        categories = Category.all()
        categories.ancestor(cat_key)

        for category in categories:
            items = category.items
            if new_item not in items:
                items.append(new_item)
                category.put()
            break


    def add_category(self, new_cat):
        currt_user = users.get_current_user()
        accounts = Account.all()
        accounts.filter("user_id =", currt_user.nickname())

        for account in accounts:
            cat = Category(key_name=new_cat, parent=account, cat_name=new_cat)
            cat.put()
            break
            

    def manage_page(self):
        currt_user = users.get_current_user()

        account_key = db.Key.from_path('Account', currt_user.nickname())
        categories = Category.all()
        categories.ancestor(account_key)

        template_values = {
            'categories': categories
        }
        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.out.write(template.render(path, template_values))


    def account_page(self):
        accounts = Account.all()
        template_values = {
            'accounts': accounts
        }
        path = os.path.join(os.path.dirname(__file__), 'accounts.html')
        self.response.out.write(template.render(path, template_values))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/option', OptionHandler)
], debug=True)
















