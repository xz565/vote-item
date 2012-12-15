class Account(db.Model):
    user_id = db.StringProperty()


class Category(db.Model):
    cat_name = db.StringProperty()


class Item(db.Model):
	item_name = db.StringProperty()
    win = db.IntegerProperty()
    lose = db.IntegerProperty()