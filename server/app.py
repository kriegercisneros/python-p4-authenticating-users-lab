#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
#this is where my session is defined.  this encrypts session data before sotring it client
#side, which is then decrypted when it is sent back to the server.  this is stored in 
#cookies
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401
    
class Login(Resource):
    def post(self, id):
        #gets a username from the request's JSON
        #retrieves the user by username
        #sets the session's user_id value to the user's id
        #returns the user as JSON with a 202 code
        #why are we using get_json() if we are fetching from the session???? 
        #because i am not fetching from the session here, i am comparing the ['username']
        #key from my user table.  No User.username is from the users table in the database
        #['username'] is accessing the value associated with the username key that is 
        #being jsonified and returned
        user=User.query.filter(User.username == request.get_json()['username'].first())
        #this defines the user_id in my sessions to equal the entered user id from the 
        #client side after the client makes a post request to retrieve their user inform
        #-ation when they visit the login page
        session['user_id']=user.id
        return jsonify(user.to_dict())
    
class CheckSession(Resource):
    def get(self):
        #the session object behaves like a dictionary, so we can view its contents
        #by iterating over its keys and values 
        #where do i fucking define a fucking session???
        user=User.query.filter(User.id==session.get('user_id')).first()
        if user:
            return jsonify(user.to_dict())
        else:
            return jsonify({'message':'401:Not Authorized'}), 401
        
class Logout(Resource):
    def delete(self):
        #simply setting the key of user_id in sessions equal to none
        session['user_id'] = None
        return jsonify({'message': '204: No Content'}), 204
        

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Logout, '/logout')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
