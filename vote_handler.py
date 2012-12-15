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
        voted_item = self.request.get("voted_item")
        item1 = self.request.get("item1")
        item2 = self.request.get("item2")

        currt_user = users.get_current_user()
        accounts = Account.all()
        accounts.filter("user_id =", currt_user.nickname())

        vote = ''

        for account in accounts:
            vote = Vote(parent=account)
            vote.category = category
            vote.owner = owner
            break


        if voted_item == item1:
            self.response.out.write("""
                <html>
                    You voted for %s over %s
                    <br><br>
                </html>
                """ %(item1, item2))
            vote.win = item1
            vote.lose = item2
            vote.put()

        elif voted_item == item2:
            self.response.out.write("""
                <html>
                    You voted for %s over %s
                    <br><br>
                </html>
                """ %(item2, item1))
            vote.win = item2
            vote.lose = item1
            vote.put()
        

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
