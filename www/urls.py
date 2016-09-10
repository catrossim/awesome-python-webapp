from transwarp.web import get, view
from models import User, Blog, Comment

@view('test_user.html')
@get('/')
def test_user():
    users = User.find_all()
    return dict(users=users)
    
