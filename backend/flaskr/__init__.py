
import json
import os
from typing import final
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import db

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def format_categories(categories):

    response = {}

    for category in categories:
        response[category.id] = category.type
    
    return response

def paginate(request, data):

    #Get query parameter --page
    page = request.args.get('page',1, type=int)

    start = (page - 1) * QUESTIONS_PER_PAGE

    end = page * QUESTIONS_PER_PAGE

    questions = [i.format() for i in data]

    response = questions[start:end]

    return response


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    CORS(app, resources={r"/api/*": {"origin":"*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Autorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,PATCH,POST,DELETE,OPTIONS')

        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def fetch_categories():

        #fetch all categories
        categories = Category.query.all()

        return jsonify({
            'status': True,
            'categories': format_categories(categories)
        })
   
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def fetch_questions():

        try:

            #Get all questions
            questions = Question.query.all()
            #Get the total number of questions
            lenOfQuestions = len(questions)

            #Get all categories
            categories = format_categories(Category.query.all())

            return jsonify({
                'status': True,
                'questions': paginate(request, questions),
                'total_questions': lenOfQuestions,
                'categories': categories
            })
        except Exception as e:
            db.session.rollback()
            print(e)
            abort(402)
            
        finally:
            db.session.close()

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        try:
            #FIND the question by id
            question = Question.query.filter_by(id=id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })

        except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():

        # get all data from request
        data = request.get_json()

        #validate the request data since all fields are required
        if not ('question' in data and 'answer' in data and
                'difficulty' in data and 'category' in data):
            abort(422)
        
        #check for emptiness
        for i in data:
            if data[i] == '' or data[i] == None:
                abort(422)
        
        #Get the values from request

        question = data['question']
        answer = data['answer']
        difficulty = data['difficulty']
        category = data['category']

        try:
            #Create a new question
            question = Question(question=question, answer=answer,
                                difficulty=difficulty,
                                category=category)
            question.insert()

            # get all questions and paginate
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate(request, selection)

            return jsonify({
                'success': True,
                'message': 'Question added successfully'
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_question():

        term = request.get_json().get('searchTerm', None)

        try:
            
            questions = Question.query.filter(Question.question.ilike(f"%{term}%")).all()

            return jsonify({
                'status': True,
                'questions': paginate(request,questions),
                'total_questions': len(questions),
                'current_category': None
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def fetch_category_questions(id):
        
        try:
            #get category
            category = Category.query.get(id)

            if not category:
                abort(404)
            
            questions = Question.query.filter_by(category=id).all()
            lenOfQuestions = len(Question.query.all())

            return jsonify({
                'status': True,
                'total_questions': lenOfQuestions,
                'questions': paginate(request, questions),
                'current_category': category.type
            })
        except Exception as e:
            print(e)
            abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():

        try:
            data = request.get_json()

            category = data.get('quiz_category', None)
            previous_questions = data.get('previous_questions', None)

            if category == None or previous_questions == None:
                abort(422)

            #Check when all questions is selected
            if category['type'] == 'click' and category['id'] == 0:
                questions = Question.query.filter(Question.id.notin_((previous_questions))).all()

            # Filter out by category selected
            else:
                category_id = category['id']
                questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((previous_questions))).all()

            #now let play the game by selecting questions that are available

            if not len(questions):
                response = None
            else:
                choice = random.randrange(0, len(questions))
                response = questions[choice].format()
        
            return jsonify({
                'success': True,
                'question': response
            })
        except Exception as e:
            print(e)
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            'status': False,
            'error': 400,
            'message': 'Bad request'
        }),400

    @app.errorhandler(404)
    def not_found_request(error):

        return jsonify({
            'status': False,
            'error': 404,
            'message': 'Not found.'
        }),404

    @app.errorhandler(422)
    def unprocessable_request(error):

        return jsonify({
            'status': False,
            'error': 422,
            'message': 'Unprocessable request' 
        }), 422

    @app.errorhandler(500)
    def server_error_request(error):
        
        return jsonify({
            'status': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500


    return app

