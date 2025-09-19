from marshmallow import Schema, fields, validate

class ProductSchema(Schema):
    # 'name' is required, must be between 2 and 120 chars
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=120)
    )
    # 'price' is required and must be a positive number
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0, error="Price must be a positive number.")
    )
    # 'stock' must be a positive integer, defaults to 0 if not provided
    stock = fields.Integer(
        load_default=0,
        validate=validate.Range(min=0, error="Stock cannot be negative.")
    )
    
    # Optional fields
    description = fields.String(required=False)
    animal_type = fields.String(required=False)
    category = fields.String(required=False)
    dosage_info = fields.String(required=False)
    is_active = fields.Boolean(load_default=True)