import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Product, Cart, Order, OrderItem
from flask_jwt_extended import create_access_token

class TestConfig:
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        
        product1 = Product(
            name='测试商品1',
            description='测试商品描述',
            price=100.0,
            stock=10,
            category='测试'
        )
        product2 = Product(
            name='测试商品2',
            description='测试商品描述',
            price=200.0,
            stock=5,
            category='测试'
        )
        db.session.add(product1)
        db.session.add(product2)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}

class TestOrderCreation:
    """订单创建测试"""
    
    def test_create_order_success(self, app, client, auth_headers):
        """
        测试：创建订单成功
        预期：订单创建成功，购物车清空，库存减少
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            product1 = Product.query.filter_by(name='测试商品1').first()
            product2 = Product.query.filter_by(name='测试商品2').first()
            
            cart1 = Cart(user_id=user.id, product_id=product1.id, quantity=2)
            cart2 = Cart(user_id=user.id, product_id=product2.id, quantity=1)
            db.session.add(cart1)
            db.session.add(cart2)
            db.session.commit()
        
        order_data = {
            'address': {
                'name': '张三',
                'phone': '13800138000',
                'address': '北京市朝阳区xxx街道'
            },
            'payment_method': '微信'
        }
        
        response = client.post('/api/orders', json=order_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'order' in data
        assert data['order']['status'] == '待支付'
        assert data['order']['total_amount'] == 400.0
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            cart_count = Cart.query.filter_by(user_id=user.id).count()
            assert cart_count == 0
            
            product1 = Product.query.filter_by(name='测试商品1').first()
            product2 = Product.query.filter_by(name='测试商品2').first()
            assert product1.stock == 8
            assert product2.stock == 4
            
            order = Order.query.filter_by(user_id=user.id).first()
            assert order is not None
            assert order.order_items.count() == 2
    
    def test_create_order_insufficient_stock(self, app, client, auth_headers):
        """
        测试：库存不足时创建订单
        预期：订单创建失败，返回错误，购物车保留，库存不变
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            product = Product.query.filter_by(name='测试商品1').first()
            
            cart = Cart(user_id=user.id, product_id=product.id, quantity=100)
            db.session.add(cart)
            db.session.commit()
        
        order_data = {
            'address': {
                'name': '张三',
                'phone': '13800138000',
                'address': '北京市朝阳区xxx街道'
            }
        }
        
        response = client.post('/api/orders', json=order_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '库存不足' in data['error']
        
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            cart_count = Cart.query.filter_by(user_id=user.id).count()
            assert cart_count == 1
            
            product = Product.query.filter_by(name='测试商品1').first()
            assert product.stock == 10
            
            order_count = Order.query.filter_by(user_id=user.id).count()
            assert order_count == 0
    
    def test_create_order_unauthorized(self, app, client):
        """
        测试：未登录时创建订单
        预期：返回401错误
        """
        order_data = {
            'address': {
                'name': '张三',
                'phone': '13800138000',
                'address': '北京市朝阳区xxx街道'
            }
        }
        
        response = client.post('/api/orders', json=order_data)
        
        assert response.status_code == 401
    
    def test_create_order_empty_cart(self, app, client, auth_headers):
        """
        测试：购物车为空时创建订单
        预期：返回错误
        """
        order_data = {
            'address': {
                'name': '张三',
                'phone': '13800138000',
                'address': '北京市朝阳区xxx街道'
            }
        }
        
        response = client.post('/api/orders', json=order_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert '购物车为空' in data['error']
    
    def test_create_order_missing_address(self, app, client, auth_headers):
        """
        测试：缺少地址信息
        预期：返回错误
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            product = Product.query.filter_by(name='测试商品1').first()
            
            cart = Cart(user_id=user.id, product_id=product.id, quantity=1)
            db.session.add(cart)
            db.session.commit()
        
        response = client.post('/api/orders', json={}, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert '请提供收货地址' in data['error']


class TestOrderQuery:
    """订单查询测试"""
    
    def test_get_orders_list(self, app, client, auth_headers):
        """
        测试：获取订单列表
        预期：返回用户的订单列表
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            order = Order(
                user_id=user.id,
                total_amount=100.0,
                status='待支付',
                address_json='{"name": "张三", "phone": "13800138000", "address": "测试地址"}'
            )
            db.session.add(order)
            db.session.commit()
        
        response = client.get('/api/orders', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) == 1
        assert data['items'][0]['status'] == '待支付'
    
    def test_get_order_detail(self, app, client, auth_headers):
        """
        测试：获取订单详情
        预期：返回订单详情，包含订单项
        """
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            product = Product.query.filter_by(name='测试商品1').first()
            
            order = Order(
                user_id=user.id,
                total_amount=200.0,
                status='待支付',
                address_json='{"name": "张三", "phone": "13800138000", "address": "测试地址"}'
            )
            db.session.add(order)
            db.session.flush()
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=2,
                price=100.0
            )
            db.session.add(order_item)
            db.session.commit()
            
            order_id = order.id
        
        response = client.get(f'/api/orders/{order_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == order_id
        assert 'items' in data
        assert len(data['items']) == 1
        assert data['items'][0]['quantity'] == 2
    
    def test_get_order_not_found(self, app, client, auth_headers):
        """
        测试：获取不存在的订单
        预期：返回404
        """
        response = client.get('/api/orders/99999', headers=auth_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert '订单不存在' in data['error']
