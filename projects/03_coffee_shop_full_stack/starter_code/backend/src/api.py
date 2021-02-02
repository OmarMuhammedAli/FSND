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
@TODO- uncomment the following line to initialize the datbase (Done!)
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


def format_recipe(recipe):
    """
    Makes sure that every recipe is formatted correctly before being saved to the db
    """
    if not isinstance(recipe, (list, dict)):
        return None
    if isinstance(recipe, list):
        for r in recipe:
            name, color, parts = r.get('name', None), r.get('color', None), r.get('parts', None)
            if not isinstance(name, str):
                return None
            if not isinstance(color, str):
                return None
            if not isinstance(parts, (int, float)):
                return None
        return json.dumps(recipe)
    else:
        name, color, parts = recipe.get('name', None), recipe.get('color', None), recipe.get('parts', None)
        if not isinstance(name, str):
            return None
        if not isinstance(color, str):
            return None
        if not isinstance(parts, (int, float)):
            return None
        return json.dumps(list(recipe))
            

# ROUTES
'''
@TODO- implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure (Done!)
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        if len(drinks) < 1:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        abort(404)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try: 
        drinks = Drink.query.order_by(Drink.id).all()
        if len(drinks) < 1:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        abort(404)

'''
@TODO- implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure(Done!)
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    try:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if title is None or recipe is None:
            abort(400)

        formatted_recipe = format_recipe(recipe)

        if formatted_recipe is None:
            abort(422)

        drink = Drink(title=title, recipe=formatted_recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except:
        abort(422)
        



'''
@TODO- implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure(Done!)
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
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
            drink.recipe = formatted_recipe
        
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)

        


# '''
# @TODO implement endpoint
#     DELETE /drinks/<id>
#         where <id> is the existing model id
#         it should respond with a 404 error if <id> is not found
#         it should delete the corresponding row for <id>
#         it should require the 'delete:drinks' permission
#     returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
#         or appropriate status code indicating reason for failure
# '''



# # Error Handling
# '''
# Example error handling for unprocessable entity
# '''


@app.errorhandler(HTTPException)
def handle_HTTPException(error):
    return jsonify({
        "success": False,
        "error": error.code,
        "message": error.name
    }), error.code


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


@app.errorhandler(AuthError)
def handle_AuthError(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    }), error.status_code
