from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.cart_service import CartService

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    """
    获取用户购物车
    ---
    tags:
      - 购物车
    security:
      - Bearer: []
    responses:
      200:
        description: 返回购物车列表
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    carts = CartService.get_user_cart(user_id)
    total = CartService.get_cart_total(user_id)
    return jsonify({
        'items': carts,
        'total': total
    }), 200

@cart_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    """
    添加商品到购物车
    ---
    tags:
      - 购物车
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - product_id
          properties:
            product_id:
              type: integer
              description: 商品ID
            quantity:
              type: integer
              default: 1
              description: 数量
    responses:
      200:
        description: 添加成功
      400:
        description: 添加失败
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'product_id' not in data:
        return jsonify({'error': '请提供商品ID'}), 400
    
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    cart, error = CartService.add_to_cart(user_id, product_id, quantity)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': '添加成功',
        'item': cart.to_dict()
    }), 200

@cart_bp.route('/cart/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart(product_id):
    """
    更新购物车商品数量
    ---
    tags:
      - 购物车
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: 商品ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - quantity
          properties:
            quantity:
              type: integer
              description: 数量（为0时移除）
    responses:
      200:
        description: 更新成功
      400:
        description: 更新失败
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return jsonify({'error': '请提供数量'}), 400
    
    quantity = data.get('quantity')
    cart, error = CartService.update_cart_item(user_id, product_id, quantity)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': '更新成功'}), 200

@cart_bp.route('/cart/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    """
    从购物车移除商品
    ---
    tags:
      - 购物车
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: 商品ID
    responses:
      200:
        description: 移除成功
    """
    user_id = int(get_jwt_identity())
    CartService.remove_from_cart(user_id, product_id)
    return jsonify({'message': '移除成功'}), 200
