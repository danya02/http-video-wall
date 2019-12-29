from flask import Flask
from peewee import *

db = SqliteDatabase('clients.db', pragmas={'foreign_keys':1})

class MyModel(Model):
    class Meta:
        database = db


class Image(MyModel):
    name = TextField()
    source_blob = BlobField()

class Thumbnail(MyModel):
    source = ForeignKeyField(Image, backref='thumbnails', unique=True)
    blob = BlobField()

class Offset(MyModel):
    x = IntegerField()
    y = IntegerField()

class Viewer(MyModel):
    vid = IntegerField(unique=True)
    offset = ForeignKeyField(Offset)



app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/<int:vid>')
def serve_view(vid):
    return 'Hello viewer id '+str(vid)

@app.route('/pic/<int:vid>/<int:width>/<int:height>')
def serve_picture(vid,width,height):
    return 'Will serve picture to viewer '+str(vid)+' with dimensions '+str((width, height))

if __name__=='__main__':
    app.run('0.0.0.0','5000')
