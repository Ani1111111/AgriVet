from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from auth.models import User
from products.models import Product

products_bp = Blueprint('products', __name__)

def _require_admin():
    uid = get_jwt_identity()
    user = User.query.get(uid)
    if not user or user.role != 'admin':
        return None
    return user

@products_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    # admin-only
    if not _require_admin():
        return jsonify({"error": "Admin only"}), 403

    data = request.get_json() or {}
    if not data.get('name') or data.get('price') is None:
        return jsonify({"error": "name and price are required"}), 400

    p = Product(
        name=data['name'].strip(),
        description=data.get('description'),
        animal_type=data.get('animal_type'),
        category=data.get('category'),
        dosage_info=data.get('dosage_info'),
        price=float(data.get('price', 0)),
        stock=int(data.get('stock', 0)),
        is_active=bool(data.get('is_active', True))
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"message": "Product created", "id": p.id}), 201


@products_bp.route('/products', methods=['GET'])
def list_products():
    q = Product.query
    # simple filters
    animal = request.args.get('animal_type')
    cat = request.args.get('category')
    if animal:
        q = q.filter_by(animal_type=animal)
    if cat:
        q = q.filter_by(category=cat)

    items = q.filter_by(is_active=True).order_by(Product.id.desc()).all()
    return jsonify([
        {
            "id": x.id, "name": x.name, "price": x.price, "stock": x.stock,
            "animal_type": x.animal_type, "category": x.category
        } for x in items
    ]), 200


@products_bp.route('/products/<int:pid>', methods=['GET'])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify({
        "id": p.id, "name": p.name, "description": p.description,
        "animal_type": p.animal_type, "category": p.category,
        "dosage_info": p.dosage_info, "price": p.price,
        "stock": p.stock, "is_active": p.is_active
    }), 200


@products_bp.route('/products/<int:pid>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_product(pid):
    if not _require_admin():
        return jsonify({"error": "Admin only"}), 403

    p = Product.query.get_or_404(pid)
    data = request.get_json() or {}
    for field in ["name","description","animal_type","category","dosage_info","price","stock","is_active"]:
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    return jsonify({"message": "Product updated"}), 200


@products_bp.route('/products/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    if not _require_admin():
        return jsonify({"error": "Admin only"}), 403

    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200
