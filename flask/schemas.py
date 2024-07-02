from marshmallow import fields, Schema


class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    deposit = fields.Integer()
    role = fields.Integer()




class ProductSchema(Schema):
    id = fields.Integer()
    product_name = fields.String()
    amount_available = fields.Integer()
    cost  = fields.Integer()
    description = fields.String()
    seller_id = fields.Integer()
