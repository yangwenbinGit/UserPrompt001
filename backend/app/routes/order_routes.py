from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_service import OrderService

order_bp = Blueprint('orders', __name__)

@order_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    """
    创建订单
    ---
    tags:
      - 订单
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - address
          properties:
            address:
              type: object
              required:
                - name
                - phone
                - address
              properties:
                name:
                  type: string
                  description: 收货人姓名
                phone:
                  type: string
                  description: 收货人电话
                address:
                  type: string
                  description: 收货地址
            payment_method:
              type: string
              enum: [微信, 支付宝]
              description: 支付方式（可选）
    responses:
      201:
        description: 订单创建成功
        schema:
          type: object
          properties:
            message:
              type: string
            order:
              $ref: '#/definitions/Order'
      400:
        description: 创建失败（购物车为空、库存不足等）
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'address' not in data:
        return jsonify({'error': '请提供收货地址'}), 400
    
    address = data.get('address')
    required_fields = ['name', 'phone', 'address']
    if not all(field in address for field in required_fields):
        return jsonify({'error': '地址信息不完整，需要姓名、电话和地址'}), 400
    
    payment_method = data.get('payment_method')
    
    order, error = OrderService.create_order(user_id, address, payment_method)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': '订单创建成功',
        'order': order.to_dict()
    }), 201

@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """
    获取当前用户的订单列表（支持分页）
    ---
    tags:
      - 订单
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: 页码
      - name: per_page
        in: query
        type: integer
        default: 10
        description: 每页数量
    responses:
      200:
        description: 返回订单列表
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                $ref: '#/definitions/Order'
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
            per_page:
              type: integer
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = OrderService.get_user_orders(user_id, page, per_page)
    return jsonify(result), 200

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """
    获取订单详情
    ---
    tags:
      - 订单
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 订单ID
    responses:
      200:
        description: 返回订单详情
        schema:
          $ref: '#/definitions/Order'
      404:
        description: 订单不存在
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    order = OrderService.get_order_by_id(order_id, user_id)
    
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    return jsonify(order.to_dict()), 200

@order_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """
    更新订单状态（模拟支付/取消）
    ---
    tags:
      - 订单
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: 订单ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [待支付, 已支付, 已取消]
              description: 订单状态
    responses:
      200:
        description: 更新成功
      400:
        description: 更新失败
      404:
        description: 订单不存在
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': '请提供状态'}), 400
    
    status = data.get('status')
    valid_statuses = ['待支付', '已支付', '已取消']
    if status not in valid_statuses:
        return jsonify({'error': f'无效的状态，有效值: {valid_statuses}'}), 400
    
    order = OrderService.get_order_by_id(order_id, user_id)
    if not order:
        return jsonify({'error': '订单不存在'}), 404
    
    updated_order, error = OrderService.update_order_status(order_id, status)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': '状态更新成功',
        'order': updated_order.to_dict()
    }), 200
