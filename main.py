#!/usr/bin/env python

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import webapp2


from models import Account
from models import Category
from models import Item

from vote_handler import VoteHandler


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



class ManageHandler(webapp2.RequestHandler):
    def get(self):
        currt_user = users.get_current_user()
        account_key = db.Key.from_path('Account', currt_user.nickname())
        account = db.get(account_key)

        new_cat = self.request.get("new_cat")
        edit = self.request.get("edit")
        new_item = self.request.get("new_item")

        if new_cat:
            self.add_category(new_cat, account)
            self.manage_page(account_key)

        if edit:
            self.edit(currt_user, account)

        if new_item:
            self.add_item(new_item)
            self.edit(currt_user, account)


    def add_item(self, new_item):
        currt_user = users.get_current_user()
        cat_name = self.request.get("cat_name")
        cat_key = db.Key.from_path('Account', currt_user.nickname(), 'Category', cat_name)

        category = db.get(cat_key)

        items = Item.all()
        items.ancestor(cat_key)
        items.filter("item_name =", new_item)


        if items.count() == 0:
            item = Item(key_name=new_item, parent=category, item_name=new_item)
            item.win = 0
            item.lose = 0
            item.put()


    def edit(self, currt_user, account):
        cat_name = self.request.get("cat_name")
        category_key = db.Key.from_path('Account', currt_user.nickname(), 'Category', cat_name)
        category = db.get(category_key)
        
        items = Item.all()
        items.ancestor(category_key)

        template_values = {
            'account': account,
            'category': category,
            'items': items,
            'logout_url': users.create_logout_url("/")
        }

        path = os.path.join(os.path.dirname(__file__), 'edit.html')
        self.response.out.write(template.render(path, template_values))


    def add_category(self, new_cat, account):
        cat = Category(key_name=new_cat, parent=account, cat_name=new_cat)
        cat.put()


    def manage_page(self, account_key):
        categories = Category.all()
        categories.ancestor(account_key)

        template_values = {
            'categories': categories,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/option', OptionHandler),
    ('/manage', ManageHandler),
    ('/vote', VoteHandler)
], debug=True)

