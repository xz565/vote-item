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
        results = self.request.get("results")

        if results:
            self.show_results(account, category)

        elif vote:
            self.do_vote(account, category)
            self.vote_page(category, account)

        elif skip:
            self.vote_page(category, account)

        elif category:
            self.vote_page(category, account)
        
        elif account:
            self.choose_category_page(account)



    def show_results(self, account, category):
        items = Item.all()
        cat_key = db.Key.from_path("Account", account, "Category", category)
        items.ancestor(cat_key)
        
        self.response.out.write("<html>")
        for item in items.run():

            percent = ''
            if (item.win + item.lose) == 0:
                percent = '-'
            else:
                percent = item.win//(item.win+item.lose)

            self.response.out.write("""
                    <h2>Item name: %s,
                    win: %s,
                    lose: %s,
                    percentage: %s</h2>
                """ %(item.item_name, item.win, item.lose, percent))
            
        self.response.out.write("<h3>Back to <a href='/'> Home </a></h3>")

        self.response.out.write("</html>")


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
                    <h1>You voted for <i>%s</i> over <i>%s</i></h1>
                    <br><br>
                </html>
                """ %(item1_name, item2_name))

        elif voted_item_name == item2_name:
            item2.win = item2.win + 1
            item1.lose = item1.lose + 1
            self.response.out.write("""
                <html>
                    <h1>You voted for <i>%s</i> over <i>%s</i></h1>
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
            self.response.out.write("<html><h2>Item number smaller than two, \
                            please choose another category</h2></html>")
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
