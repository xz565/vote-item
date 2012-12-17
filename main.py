#!/usr/bin/env python

import os, urllib

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

from models import Account
from models import Category
from models import Item

import xml.dom.minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment

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


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads()  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        #self.redirect('/serve/%s' % blob_info.key())
        blob_key = blob_info.key()
        blob_reader = blobstore.BlobReader(blob_key)
        document = blob_reader.read()
        #self.response.out.write(document)
        dom = xml.dom.minidom.parseString(document)
        names = dom.getElementsByTagName("NAME")

        xml_cat_name = names[0].toxml() 
        xml_cat_name = xml_cat_name.replace("<NAME>", "")
        xml_cat_name = xml_cat_name.replace("</NAME>", "")

        xml_item_names = []
        for i in range(1, len(names)):
            name = names[i].toxml()
            name = name.replace("<NAME>", "")
            name = name.replace("</NAME>", "")
            xml_item_names.append(name)

        currt_user = users.get_current_user()
        account_key = db.Key.from_path('Account', currt_user.nickname())
        account = db.get(account_key)
        categories = Category.all()
        categories.ancestor(account_key)

        cat_names = []
        for category in categories.run():
            cat_names.append(category.cat_name)

        ###
        if xml_cat_name in cat_names:
            items = Item.all()
            category = categories.filter("cat_name =", xml_cat_name)
            category = category.get()
            category_key = category.key()
            
            items = items.ancestor(category_key)
            item_names = []
            for item in items:
                item_names.append(item.item_name)

            ### add new items
            for item_name in xml_item_names:
                if item_name not in item_names:
                    item = Item(key_name=item_name, parent=category, item_name=item_name)
                    item.put()

            ### delete old items
            for item_name in item_names:
                if item_name not in xml_item_names:
                    items = Item.all()
                    items = items.ancestor(category_key)
                    items.filter("item_name =", item_name)
                    item = items.get()
                    item.delete()

        ### if new category
        else:
            cat = Category(key_name=xml_cat_name, parent=account, cat_name=xml_cat_name)
            cat.put()
            for xml_item_name in xml_item_names:
                item = Item(key_name=xml_item_name, parent=cat, item_name=xml_item_name)
                item.win = 0
                item.lose = 0
                item.put()



class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    pass


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/option', OptionHandler),
    ('/manage', ManageHandler),
    ('/vote', VoteHandler),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler)
], debug=True)

