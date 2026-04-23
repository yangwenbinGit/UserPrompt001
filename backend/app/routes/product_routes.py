from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService

product_bp = Blueprint('products', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """
    获取商品列表（支持分页）
    ---
    tags:
      - 商品
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
        description: 返回商品列表
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = ProductService.get_all_products(page, per_page)
    return jsonify(result), 200

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    获取商品详情
    ---
    tags:
      - 商品
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: 商品ID
    responses:
      200:
        description: 返回商品详情
      404:
        description: 商品不存在
    """
    product = ProductService.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': '商品不存在'}), 404
    return jsonify(product.to_dict()), 200
