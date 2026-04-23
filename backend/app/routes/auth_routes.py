from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    ---
    tags:
      - 认证
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              description: 用户名
            email:
              type: string
              description: 邮箱
            password:
              type: string
              description: 密码
    responses:
      201:
        description: 注册成功
      400:
        description: 注册失败
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据无效'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': '请填写所有必填字段'}), 400
    
    user, error = AuthService.register(username, email, password)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    ---
    tags:
      - 认证
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 用户名
            password:
              type: string
              description: 密码
    responses:
      200:
        description: 登录成功，返回JWT token
      401:
        description: 登录失败
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据无效'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'error': '请输入用户名和密码'}), 400
    
    user, error = AuthService.login(username, password)
    if error:
        return jsonify({'error': error}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    获取当前用户信息
    ---
    tags:
      - 认证
    security:
      - Bearer: []
    responses:
      200:
        description: 返回用户信息
      401:
        description: 未授权
    """
    user_id = int(get_jwt_identity())
    user = AuthService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict()), 200
