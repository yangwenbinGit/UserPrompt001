from app.models import Product
from app import db

class ProductService:
    @staticmethod
    def get_all_products(page=1, per_page=10):
        pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }
    
    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)
    
    @staticmethod
    def create_product(data):
        product = Product(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            stock=data.get('stock', 0),
            image_url=data.get('image_url'),
            category=data.get('category')
        )
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update_stock(product_id, quantity):
        product = Product.query.get(product_id)
        if not product:
            return False
        if product.stock < quantity:
            return False
        product.stock -= quantity
        db.session.commit()
        return True
