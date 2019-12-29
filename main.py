from flask import Flask, send_file, abort, url_for, render_template, request
from peewee import *
import io
import uuid
import pygame

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

db.create_tables([Image,Thumbnail,Offset,Viewer])


app = Flask(__name__)

@app.route('/')
def config():
    return render_template('config.html')

@app.route('/<int:vid>')
def serve_view(vid):
    return 'Hello viewer id '+str(vid)

@app.route('/pic/<int:vid>/<int:width>/<int:height>')
def serve_page(vid,width,height):
    return 'Will serve picture to viewer '+str(vid)+' with dimensions '+str((width, height))

@app.route('/add_picture', methods=['POST'])
def add_picture():
    f = request.files['file']
    with db.atomic():
        buf = io.BytesIO()
        f.save(buf)
        image = Image.create(name=f.filename, source_blob=buf.getvalue())
        buf.seek(0)
        surf = pygame.image.load(buf, f.filename)
        if surf.get_width()>surf.get_height():
            fac = 400/surf.get_width()
            h = int(surf.get_height()*fac)
            newsurf = pygame.transform.smoothscale(surf, (400,h))
        else:
            fac = 400/surf.get_height()
            w = int(surf.get_width()*fac)
            newsurf = pygame.transform.smoothscale(surf, (w,400))
        name = '/tmp/'+str(uuid.uuid4())+'.png'
        pygame.image.save(newsurf, name)
        with open(name, 'rb') as o:
            thumb = Thumbnail.create(source=image, blob=o.read())
            thumb.save()
    return str(image.id)

@app.route('/image/<int:pic_id>')
def serve_image(pic_id):
    try:
        img = Image.get(Image.id==pic_id)
    except Image.DoesNotExist:
        return abort(404)
    return send_file(io.BytesIO(img.source_blob),'image/'+img.name.split('.')[-1])

@app.route('/thumb/<int:pic_id>')
def serve_thumb(pic_id):
    try:
        img = Thumbnail.get(Thumbnail.source==pic_id)
    except Thumbnail.DoesNotExist:
        return abort(404)
    return send_file(io.BytesIO(img.blob),'image/png')


if __name__=='__main__':
    app.run('0.0.0.0','5000')
