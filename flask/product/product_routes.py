from app.main import db
from flask import Blueprint, jsonify, request 
from logs.logging_aspects import view_logging_aspect
from utils.role_required_decorator import role_required
from utils.exception_handler_decorator import CustomException
from utils.exception_handler_decorator import handle_exceptions
from flask_jwt_extended import jwt_required,current_user
from schemas import ProductSchema
from product.product_models import Product
from .product_constants import (
    PRODUCT_LOGGER,
    PRODUCT_LOG_FILE_PATH
)


product_bp = Blueprint("product", __name__)


@handle_exceptions
@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@product_bp.get("")
@jwt_required()
def list():
    """
    list all products.

    Returns:
    list of products 

    """
    products = Product.query.all()
    result = ProductSchema().dump(products, many=True)
    return (
        jsonify(
            {
                "products": result,
            }
        ),
        200,
    )

@handle_exceptions
@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@product_bp.get("/<int:product_id>")
@jwt_required()
def get(product_id):
    """
    get product by id .

    param :product_id:

    Returns:
    "tokens":  product_id data in success
    message error in fail

    """
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@handle_exceptions
@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@product_bp.post("")
@jwt_required()
@role_required('seller')
def create_product():
    """
    create product .

    role_required :only seller role:

    Returns:
     product data in success

    """
    data = request.get_json()
    if not data or  'product_name' not in data or 'cost' not in data :
        return jsonify({"message": "please required fields(product_name,cost,email)"}), 400

    new_product = Product(product_name=data.get('product_name'),
                          cost=data.get('cost'),
                          amount_available=data.get('amount_available'),
                          description=data.get('description', ''),
                          seller_id=current_user.id
                          )
    db.session.add(new_product)
    db.session.commit()    
    result = ProductSchema().dump(new_product)
    return (
        jsonify(
            {
                "product": result,
            }
        ),
        200,
    )



@handle_exceptions
@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@product_bp.put("/<int:product_id>")
@jwt_required()
@role_required('seller')
def update_product(product_id):
    """
    update product .

    role_required :only seller role:

    Returns:
    product new data in success
    error message in fail
    
    """
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        data = request.get_json()
        product.product_name = data.get('product_name', product.product_name)
        product.amount_available = data.get('amount_available', product.amount_available)
        product.cost = data.get('cost', product.cost)
        product.description = data.get('description', product.description)
        product.seller_id = data.get('seller_id', product.seller_id)

        db.session.commit()
        return jsonify(ProductSchema().dump(product))
    else:
        return jsonify({"error": "you don't have permission to access this product"}), 403




@handle_exceptions
@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@role_required('seller')
@product_bp.delete("/<int:product_id>")
def delete_product(product_id):
    """
    delete product .

    role_required :only seller role:

    Returns:
    success message in success

    """
    product = Product.query.get_or_404(product_id)
    if product.seller_id == current_user.id:
        db.session.delete(product)
        db.session.commit()
        return (
        jsonify(
            {
                "message": "product deleted" ,
            }
        ),
        200,
    )
    else:
        return jsonify({"error": "you don't have permission to access this product"}), 403



@view_logging_aspect(PRODUCT_LOGGER, PRODUCT_LOG_FILE_PATH)
@product_bp.post("/buy/product")
@jwt_required()
@role_required('buyer')
def buy_product():
    """
    make user with role buyer buy product by any amount with the money they’ve deposited. 
    
    role_required :only buyer role:

    body
    product_id: integer
    amount :integer

    Returns:
    products_purchased,total_spent data,change in success
     

    """
    data = request.get_json()
    product = Product.query.get_or_404(data.get('product_id'))
    amount= data.get('amount')
    buyer_deposit=  data.get('deposit')
    if product.amount_available < amount:
        return jsonify({"error": "not enough amount of product you want"}), 400
    
    total_cost = product.cost * amount
    if buyer_deposit < total_cost:
        return jsonify({"error": "you deposit not enough ,please add more money"}), 400

    change = buyer_deposit - total_cost
    change_coins = calculate_change(change)
   
    return jsonify(
        {
            'products_purchased': {'id': product.id, 'name': product.product_name, 'amount': amount},
            "total_spent":total_cost,
            "change": change_coins
         
         }), 400

    
    
def calculate_change(amount):
    """
    return only coin in [5, 10, 20, 50, 100]
    
    param :amount

    product_id: integer
    amount :integer

    Returns:
    change

    """
    
    coins = [ 0.5, 0.2, 0.1, 0.05]
    change = {}
    remaining = round(amount, 2)
    for coin in coins:
        count = int(remaining // coin)
        if count > 0:
            change[f'{int(coin*100)} cent'] = count
            remaining -= count * coin
    return change     