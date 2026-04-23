import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models import Order, OrderItem, Cart, Product
from app import db

class OrderService:
    @staticmethod
    def create_order(user_id, address_data, payment_method=None):
        """
        创建订单（使用数据库事务）
        流程：读取购物车 → 检查库存 → 创建订单和订单商品 → 扣减库存 → 清空购物车 → 提交事务
        """
        try:
            carts = Cart.query.filter_by(user_id=user_id).all()
            if not carts:
                return None, '购物车为空'
            
            order_items = []
            total_amount = 0.0
            
            for cart in carts:
                product = Product.query.with_for_update().get(cart.product_id)
                if not product:
                    db.session.rollback()
                    return None, f'商品 {cart.product_id} 不存在'
                
                if product.stock < cart.quantity:
                    db.session.rollback()
                    return None, f'商品 {product.name} 库存不足，当前库存: {product.stock}'
                
                item_total = product.price * cart.quantity
                total_amount += item_total
                
                order_items.append({
                    'product': product,
                    'quantity': cart.quantity,
                    'price': product.price
                })
            
            order = Order(
                user_id=user_id,
                total_amount=total_amount,
                status=Order.STATUS_PENDING,
                address_json=json.dumps(address_data, ensure_ascii=False),
                payment_method=payment_method
            )
            db.session.add(order)
            db.session.flush()
            
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product'].id,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(order_item)
                
                item_data['product'].stock -= item_data['quantity']
            
            Cart.query.filter_by(user_id=user_id).delete()
            
            db.session.commit()
            return order, None
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return None, f'数据库错误: {str(e)}'
        except Exception as e:
            db.session.rollback()
            return None, f'创建订单失败: {str(e)}'
    
    @staticmethod
    def get_user_orders(user_id, page=1, per_page=10):
        """
        获取用户订单列表（支持分页）
        """
        pagination = Order.query.filter_by(user_id=user_id)\
            .order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [order.to_dict(include_items=False) for order in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_order_by_id(order_id, user_id=None):
        """
        获取订单详情
        如果提供了 user_id，则验证订单属于该用户
        """
        query = Order.query.filter_by(id=order_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.first()
    
    @staticmethod
    def update_order_status(order_id, status):
        """
        更新订单状态
        """
        order = Order.query.get(order_id)
        if not order:
            return None, '订单不存在'
        
        order.status = status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return order, None
