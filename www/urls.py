# coding: utf-8
from transwarp.web import get, view
from models import User, Blog, Comment
from api import api
@view('test_user.html')
@get('/test_user')
def test_user():
    users = User.find_all()
    print dict(users=users)
    return dict(users=users)

@api
@get('/')
def index():
    blogs = Blog.find_all()
    # 查找登陆用户:
    user = User.find_first('where email=?', 'cat@house.com')
    return dict(blogs=blogs, user=user)
