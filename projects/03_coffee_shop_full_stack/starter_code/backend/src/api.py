import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


def format_recipe(recipe):
    """
    Makes sure that every recipe is formatted correctly before
    being saved to the db
    """
    if not isinstance(recipe, (list, dict)):
        return None
    if isinstance(recipe, list):
        for r in recipe:
            name = r.get('name', None)
            color = r.get('color', None)
            parts = r.get('parts', None)
            if not isinstance(name, str):
                return None
            if not isinstance(color, str):
                return None
            if not isinstance(parts, (int, float)):
                return None
        return recipe
    else:
        lst = []
        name = recipe.get('name', None)
        color = recipe.get('color', None)
        parts = recipe.get('parts', None)
        if not isinstance(name, str):
            return None
        if not isinstance(color, str):
            return None
        if not isinstance(parts, (int, float)):
            return None
        lst.append(recipe)
        return lst

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    Gets public info about the drinks
    return: On a successful call, returns a json object as follows:
    {
        'success': True,
        'drinks': short representation for the available drinks
    }
    """
    drinks = Drink.query.order_by(Drink.id).all()
    # if len(drinks) < 1:
    #     abort(404)
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """
    Gets detailed info about the drinks
    expects a 'get:drinks-detail' permission to be included in the payload
    params: {
        payload: json object contains the claims included in the jwt.
    }
    return: Upon a successful call:
    {
        'success': True,
        'drinks': Detailed representation of the drinks
    }
    """
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        # if len(drinks) < 1:
        #     abort(404)
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except Exception as e:
        print(e)
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
    Adds a drink in the db
    expects a 'post:drinks' permission to be included in the payload
    params: {
        payload: json object contains the claims included in the jwt.
    }
    return: Upon a successful call:
    {
        'success': True,
        'drinks': A list representation of the newely posted drink
    }
    """
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title is None or recipe is None:
            abort(400)

        formatted_recipe = format_recipe(recipe)
        if formatted_recipe is None:
            abort(422)

        drink = Drink(title=title, recipe=json.dumps(formatted_recipe))
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    """
    Updates a drink in the db
    expects a 'patch:drinks' permission to be included in the payload
    params: {
        payload: json object contains the claims included in the jwt,
        id: the id of the drink to be updated
    }
    return: Upon a successful call:
    {
        'success': True,
        'drinks': Detailed representation of the updated drink
    }
    """
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)

    body = request.get_json()
    try:
        if 'title' in body:
            drink.title = body.get('title')

        if 'recipe' in body:
            formatted_recipe = format_recipe(body.get('recipe'))
            if formatted_recipe is None:
                abort(422)
            drink.recipe = json.dumps(formatted_recipe)

        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """
    Deletes a drink from the db
    expects a 'delete:drinks' permission to be included in the payload
    params: {
        payload: json object contains the claims included in the jwt,
        id: The id of the drink to be deleted
    }
    return: Upon a successful call:
    {
            'success': True,
            'delete': The id of the deleted drink
    }
    """
    try:
        drink = Drink.query.get(id)
        if drink is None:
            abort(404)
        drink_id = drink.id
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception as e:
        print(e)
        abort(404)

# # Error Handling


@app.errorhandler(HTTPException)
def handle_HTTPException(error):
    """Handler for HTTP exceptions"""
    return jsonify({
        "success": False,
        "error": error.code,
        "message": error.name
    }), error.code


@app.errorhandler(AuthError)
def handle_AuthError(error):
    """AuthError exception hanlder"""
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    }), error.status_code
