#!/usr/bin/env python

import os, random

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import webapp2


from models import Account
from models import Category
from models import Item


class VoteHandler(webapp2.RequestHandler):
    def get(self):
        account = self.request.get("account")
        category = self.request.get("category")

        vote = self.request.get("vote")
        skip = self.request.get("skip")

        if vote:
            self.do_vote(account, category)
            self.vote_page(category, account)

        elif skip:
            self.vote_page(category, account)

        elif category:
            self.vote_page(category, account)
        
        elif account:
            self.choose_category_page(account)


    def do_vote(self, owner, category):
        voted_item_name = self.request.get("voted_item_name")
        item1_name = self.request.get("item1")
        item2_name = self.request.get("item2")

        account = self.request.get("account")
        account_key = db.Key.from_path("Account", account)

        account_items = Item.all()
        account_items = account_items.ancestor(account_key)

        item1 = ''
        item2 = ''

        for item in account_items.run():
            if item.item_name == item1_name:
                item1 = item
            if item.item_name == item2_name:
                item2 = item


        if voted_item_name == item1_name:
            item1.win = item1.win + 1
            item2.lose = item2.lose + 1
            self.response.out.write("""
                <html>
                    You voted for %s over %s
                    <br><br>
                </html>
                """ %(item1_name, item2_name))

        elif voted_item_name == item2_name:
            item2.win = item2.win + 1
            item1.lose = item1.lose + 1
            self.response.out.write("""
                <html>
                    You voted for %s over %s
                    <br><br>
                </html>
                """ %(item2_name, item1_name))

        item1.put()
        item2.put()
        

    def choose_category_page(self, account):
        account_key = db.Key.from_path('Account', account)
        categories = Category.all()
        categories.ancestor(account_key)

        template_values = {
            'account': account,
            'categories': categories,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'choose_category.html')
        self.response.out.write(template.render(path, template_values))


    def vote_page(self, category, account):
        cat_key = db.Key.from_path('Account', account, 'Category', category)
        category = db.get(cat_key)
        
        items = Item.all()
        items.ancestor(cat_key)        

        rand1 = -1;
        rand2 = -1;
        if items.count() < 2:
            self.response.out.write("Item number smaller than two")
            self.choose_category_page(account)
            return
        else:
            rand1 = random.randint(0, items.count() - 1)
            rand2 = random.randint(0, items.count() - 1)
            while rand1 == rand2:
                rand2 = random.randint(0, items.count() - 1)

        template_values = {
            'item1': items[rand1],
            'item2': items[rand2],
            'account': account,
            'category': category,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'vote.html')
        self.response.out.write(template.render(path, template_values))
