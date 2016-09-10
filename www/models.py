import time, uuid

from transwarp.db import next_id
from transwarp.orm import Model, StringField, BooleanField, FloatField, TextField


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(updatable=False, ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(updatable=False, default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(updatable=False, ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(updatable=False, default=time.time)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(updatable=False, ddl='varchar(50)')
    user_id = StringField(updatable=False, ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(updatable=False, default=time.time)

if __name__=='__main__':
    import config
    from transwarp import db
    db.create_engine(**config.configs.db)
    # user = User(id='10360',email='cat@house.com',password='1234',admin=True,name='lidong',image='/img/1.jpg')
    # user.insert()
    blog1 = Blog(
        user_id='10360',
        user_name='lidong',
        user_image='/img/1.jpg',
        name='Test',
        summary='I am LiDong and come from China, majoring in CS.',
        content='I am LiDong and come from China, majoring in CS. Happy to meet you')
    blog1.insert()
    blog2 = Blog(
        user_id='10360',
        user_name='lidong',
        user_image='/img/1.jpg',
        name='Test, Again',
        summary='Again, I am LiDong and come from China, majoring in CS.',
        content='Again,I am LiDong and come from China, majoring in CS. Happy to meet you')
    blog2.insert()
    blog3 = Blog(
        user_id='10360',
        user_name='lidong',
        user_image='/img/1.jpg',
        name='Test, Finally',
        summary='Finally, I am LiDong and come from China, majoring in CS.',
        content='Finally, I am LiDong and come from China, majoring in CS. Happy to meet you')
    blog3.insert()
