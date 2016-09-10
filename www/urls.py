from transwarp.web import get, view
from models import User, Blog, Comment

@view('test_user.html')
@get('/test_user')
def test_user():
    users = User.find_all()
    print dict(users=users)
    return dict(users=users)

@view('blogs.html')
@get('/')
def index():
    blogs = Blog.find_all()
    # 查找登陆用户:
    user = User.find_first('where email=?', 'admin@example.com')
    return dict(blogs=blogs, user=user)
