from app.models import Cart, Product
from app import db

class CartService:
    @staticmethod
    def get_user_cart(user_id):
        carts = Cart.query.filter_by(user_id=user_id).all()
        return [cart.to_dict() for cart in carts]
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        product = Product.query.get(product_id)
        if not product:
            return None, '商品不存在'
        
        existing = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if existing:
            existing.quantity += quantity
        else:
            cart = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(cart)
        
        db.session.commit()
        return Cart.query.filter_by(user_id=user_id, product_id=product_id).first(), None
    
    @staticmethod
    def update_cart_item(user_id, product_id, quantity):
        if quantity <= 0:
            return CartService.remove_from_cart(user_id, product_id)
        
        cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if not cart:
            return None, '购物车项不存在'
        
        cart.quantity = quantity
        db.session.commit()
        return cart, None
    
    @staticmethod
    def remove_from_cart(user_id, product_id):
        cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if cart:
            db.session.delete(cart)
            db.session.commit()
        return True, None
    
    @staticmethod
    def clear_cart(user_id):
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True
    
    @staticmethod
    def get_cart_total(user_id):
        carts = Cart.query.filter_by(user_id=user_id).all()
        total = 0.0
        for cart in carts:
            if cart.product:
                total += cart.product.price * cart.quantity
        return total
