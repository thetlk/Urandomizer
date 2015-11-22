# -*- coding: utf-8 -*-

import datetime
import peewee

db = peewee.SqliteDatabase(None)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Urandomization(BaseModel):
    start_time = peewee.DateTimeField(default=datetime.datetime.now)
    stop_time = peewee.DateTimeField(default=datetime.datetime.now)
    byte_count = peewee.IntegerField()
    ip_address = peewee.TextField()
    port = peewee.IntegerField()
    data = peewee.TextField()

    def __str__(self):
        return "Urandomization(start_time=%s, byte_count=%s, from=%s:%d)" % (self.start_time, self.byte_count, self.ip_address, self.port)


class BaseStorage(object):

    def _put_item(self, item_cls, **kwargs):
        try:
            with db.transaction():
                item_cls.create(**kwargs)
        except peewee.IntegrityError:
            return False
        return True


class UrandomizationStorage(BaseStorage):

    def put_urandomization(self, **kwargs):
        return self._put_item(Urandomization, **kwargs)

    def get_urandomizations(self):
        return Urandomization.select()


def setup_db(filepath):
    db.init(filepath)
    db.connect()
    for model in BaseModel.__subclasses__():
        model.create_table(fail_silently=True)
