from app.models import User
from app import db

class AuthService:
    @staticmethod
    def register(username, email, password):
        if User.query.filter_by(username=username).first():
            return None, '用户名已存在'
        if User.query.filter_by(email=email).first():
            return None, '邮箱已被注册'
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return None, '用户名或密码错误'
        return user, None
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
