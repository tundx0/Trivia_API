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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "postgres", "Western123#", "localhost:5432", self.database_name
        )
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
    # categories
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    # assertTrue or assertEqual(data['success'], True)
    def test_404_sent_requesting_non_existing_category(self):
        res = self.client().get("/categories/9999")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    # questions
    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_bad_query(self):
        res = self.client().get("/questions/?hgf=43")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_search(self):
        search_term = {"searchTerm": "a"}
        res = self.client().post("/questions/search", json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNotNone(data["questions"])

    def test_search_not_found(self):
        search_term = {"searchTerm": "wtyfhf"}
        res = self.client().post("/questions/search", json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # Delete
    def test_delete_question(self):  # delete question
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], 5)

    def test_delete_question_error(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")

    # get questions per category

    def test_get_questions_per_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_get_questions_per_category_error(self):
        res = self.client().get("/categories/a/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    # create question
    def test_create_question(self):
        res = self.client().post(
            "/questions",
            json={
                "question": "Who is the current president of the United States?",
                "answer": "Joe Biden",
                "category": 1,
                "difficulty": 1,
            },
        )
        data = json.loads(res.data)

        self.assertEquals(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

    def test_play(self):
        new_play = {
            "previous_questions": [],
            "quiz_category": {"type": "Sports", "id": 6},
        }

        res = self.client().post("/quizzes", json=new_play)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
