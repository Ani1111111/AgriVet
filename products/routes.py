from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from auth.models import User
from products.models import Product
from .schemas import ProductSchema  # <-- 1. Import schema and errors
from marshmallow import ValidationError

products_bp = Blueprint('products', __name__)
product_schema = ProductSchema()  # Schema for creating/updating one product
products_schema = ProductSchema(many=True) # Schema for listing many products

def _require_admin():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    return user if user and user.role == 'admin' else None

@products_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    # 2. Validate and deserialize input
    try:
        data = product_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400 # Return helpful errors

    # 3. Create product with validated data
    p = Product(**data) # Use dictionary unpacking
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "Product created", "id": p.id}), 201


@products_bp.route('/products', methods=['GET'])
def list_products():
    q = Product.query
    animal = request.args.get('animal_type')
    cat = request.args.get('category')
    if animal:
        q = q.filter_by(animal_type=animal)
    if cat:
        q = q.filter_by(category=cat)

    items = q.filter_by(is_active=True).order_by(Product.id.desc()).all()
    # Use the 'many=True' schema to format the output
    return jsonify(products_schema.dump(items)), 200


@products_bp.route('/products/<int:pid>', methods=['GET'])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(product_schema.dump(p)), 200


@products_bp.route('/products/<int:pid>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_product(pid):
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403

    p = Product.query.get_or_404(pid)
    json_data = request.get_json()
    
    # Validate the incoming data. partial=True allows partial updates.
    try:
        data = product_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    for key, value in data.items():
        setattr(p, key, value)
        
    db.session.commit()
    return jsonify({"message": "Product updated"}), 200


@products_bp.route('/products/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403

    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200