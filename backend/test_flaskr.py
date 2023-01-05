import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('***', '***', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "what is your favorite color", 
            "answer": "Pink", 
            "category": 2, 
            "difficulty" : 1 
            }
        self.fail_new_question = {
            "question": "what is your favorite color", 
            "answer": "Blue", 
            "category": 8, 
            "difficulty" : 1 
            }
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
    #expect error
    def test_get_paginated_question(self):
        res = self.client().get("/question")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    #successful operation
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    #expect error
    def test_question_requesting_not_valid_page(self):
        res = self.client().get("/questions?page=2000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Request is not valid")

    #successful operation
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    #expect error
    def test_get_categories_not_allowed(self):
        res = self.client().delete("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)

    #successful operation
    def test_delete_question(self):
        res = self.client().delete("/questions/15")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)    

    #expect error
    def test_question_not_found_to_delete(self):
        res = self.client().delete("/questions/1000")
        data = json.load(res.data)
        self.assertEqual(res.short_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

    #successful operation
    def test_create_new_question(self):    
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        #pass
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    #expect error
    def test_question_creation_fails(self):
        res = self.client().post("/questions", json=self.fail_new_question)
        data = json.loads(res.data)
        #pass
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    #successful operation
    def test_search_question(self):
        res = self.client().post("/search", json={"search": "who is"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 10)

    #expect error
    def test_search_questions_not_found(self):
        res = self.client().post("/search", json={{"search": "ggg aaa ttt"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'Page not found')

    #successful operation
    def test_sort_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertNotEqual(len(data["questions"]), 0)
        self.assertEqual(data["current_category"], "Science")

    #expect error
    def test_sort_questions_by_category_not_found(self):
        res = self.client().get("/categories/3000/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
    
    #successful operation
    def test_quiz(self):
        res = self.client().post("/quizzes", json={"previous_questions": [14], "quiz_category": { "type": "Geography","id": "3"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"]["category"], "3")

    #expect error
    def test_quiz_not_found(self):
        res = self.client().post("/quizzes", json={"previous_questions": [1000], "quiz_category": { "type": "AAA","id": "A"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Page not found")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()