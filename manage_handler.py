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


class ManageHandler(webapp2.RequestHandler):
    def get(self):
        currt_user = users.get_current_user()
        account_key = db.Key.from_path('Account', currt_user.nickname())
        account = db.get(account_key)

        new_cat = self.request.get("new_cat")
        edit = self.request.get("edit")
        export_XML = self.request.get("exportXML")
        import_XML = self.request.get("importXML")
        xml = self.request.get("xml")
        new_item = self.request.get("new_item")

        if new_cat:
            self.add_category(new_cat, account)
            self.manage_page(account_key)

        if edit:
            self.edit(currt_user, account)

        if export_XML:
            self.export_XML(currt_user)

        if import_XML:
            self.import_XML()

        if new_item:
            self.add_item(currt_user, new_item)
            self.edit(currt_user, account)


    def import_XML(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" \
                        name="submit" value="Submit"> </form></body></html>""")

    def export_XML(self, currt_user):
        cat_name = self.request.get("cat_name")
        cat_key = db.Key.from_path('Account', currt_user.nickname(), 'Category', cat_name)

        items = Item.all()
        items.ancestor(cat_key)

        self.response.headers['Content-Type'] = 'text/xml'
        #self.response.out.write('<?xml version="1.0"?>\n')
        self.response.out.write('<CATEGORY>\n')
        self.response.out.write('   <NAME>' + cat_name + '</NAME>\n')
        for item in items.run():
            self.response.out.write('   <ITEM>\n')
            self.response.out.write('       <NAME>' + item.item_name + '</NAME>\n')
            self.response.out.write('   </ITEM>\n')

        self.response.out.write('</CATEGORY>\n')


    def add_item(self, currt_user, new_item):
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

        items = Item.all()

        template_values = {
            'categories': categories,
            'items': items,
            'logout_url': users.create_logout_url("/")
        }
        path = os.path.join(os.path.dirname(__file__), 'manage.html')
        self.response.out.write(template.render(path, template_values))
