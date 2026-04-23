from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    jwt.init_app(app)
    
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.order_routes import order_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api')
    app.register_blueprint(order_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
        from app.models import Product
        if not Product.query.first():
            sample_products = [
                Product(name='iPhone 15', description='最新款苹果手机', price=6999.0, stock=100, category='手机'),
                Product(name='MacBook Pro', description='专业笔记本电脑', price=12999.0, stock=50, category='电脑'),
                Product(name='AirPods Pro', description='无线降噪耳机', price=1899.0, stock=200, category='配件'),
                Product(name='iPad Air', description='平板电脑', price=4599.0, stock=80, category='平板'),
                Product(name='Apple Watch', description='智能手表', price=2999.0, stock=150, category='手表'),
            ]
            for p in sample_products:
                db.session.add(p)
            db.session.commit()
    
    return app
