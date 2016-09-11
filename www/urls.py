# coding: utf-8
from transwarp.web import get, view, ctx
from models import User, Blog, Comment
from apis import api, APIError, APIValueError, APIPermissionError
import re

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

_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')
@api
@post('/user/register')
def register_user():
    i = ctx.request.input(user='',email='',password='')
    name = i.name.strip()
    email = i.email.strip()
    if not name:
        raise APIValueError('name')
    if not email:
        raise APIValueError('email')
    if not password or not _RE_MD5.match(password):
        raise APIValueError('password')
    user = User.find_first('where email=?',email)
    if user:
        raise APIError('register failed', 'email', 'email address is already in use')
    user = User(name=name,password=password,email=email,image='/img/test.jpg')
    user.insert()
    user.password = '******'
    return user

@view('register.html')
@get('/register')
def register():
    return dict()
