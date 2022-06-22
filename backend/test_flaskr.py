from enum import unique
import os
from random import random
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','abc','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

   
    def test_fetch_questions(self):
        """Tests if fetching all questions is successful"""
        response = self.client().get('/questions')
        result = json.loads(response.data)

        self.assertEqual(result['success'], True)
        self.assertEqual(response.status_code, 200)
        

    def test_200_request_valid_page(self):
        """ Tests success if user enters correct page number """
        response = self.client().get('/questions?page=1')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['success'], True)

    def test_404_request_wrong_page(self):
        """ Tests error if user enters a wrong page number """
        response = self.client().get('/questions?page=30')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result['success'], False)
        self.assertEqual(result['message'], 'Not found.')

    def test_fetch_categories(self):
        """ Tests if fetching all categories is successful"""
        response = self.client().get('/categories')
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['success'], True)

    def test_delete_question(self):
        """ Tests delete question is successful """
        # create a new question to be deleted
        question = Question(question="Should I delete it?",answer='yes', category=3, difficulty=3)
        question.insert()
        id = question.id

        response = self.client().delete('/questions/'+str(id))
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertEqual(question, None)

    def test_create_question(self):
        """Tests if create question is successful"""
        #get unique id from uuid
        unique_id = str(uuid4())
        new_question = {
            'question': 'Question: ' + unique_id,
            'answer': 'Answer: ' + unique_id,
            'difficulty': 3,
            'category': 3
        }

        #send a request to create a new question
        response = self.client().post('/questions', json=new_question)
        result = json.loads(response.data)

        #check if the question is created successfully.
        question = Question.query.filter_by(question='Question: '+unique_id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['success'], True)
        self.assertEqual(question.answer,"Answer: "+unique_id)

    def test_422_create_question(self):
        """test creation of question fails """
        
        questions_before = Question.query.all()

        #send empty data 
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        questions_after = Question.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(questions_before) == len(questions_after))

    def test_search_question(self):
        """test if search term is found and successful"""
        
        response = self.client().post('/questions/search', json={
            'searchTerm': 'What'})
        result = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['success'], True)
        self.assertTrue(len(result['questions']) > 0)
        self.assertIsNotNone(result['questions'])
        self.assertIsNotNone(result['total_questions'])

    def test_404_search_questions(self):
        """test for search not found 404"""
        response = self.client().post('/questions/search', json={
            'searchTerm': ''})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found.")

    def test_get_category_questions(self):
        """test success of getting questions by categories"""

        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_category_questions(self):
        """test for 404 error with no question from category"""
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not found.")

    def test_get_quiz(self):
        """test success of playing quiz"""

        #get one category
        category = Category.query.all()[0]

        quiz = {'previous_questions': [], 'quiz_category': {
            'type': category.type, 'id': category.id}}

        response = self.client().post('/quizzes', json=quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_get_quiz(self):
        """test 422 error if quiz game fails"""
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()