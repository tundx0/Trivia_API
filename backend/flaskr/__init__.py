import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = selection
    all_questions = []
    for question in questions:
        all_questions.append(question.format())
    current_questions = all_questions[start:end]
    return current_questions, all_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add("Access-Control-Methods", "GET,POST,DELETE")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_categories():
        main_category = Category.query.all()
        try:
            if main_category is None:
                abort(404)
            else:
                """Encountered an error where react was expecting a dictionary key: value pair and i was providing a list element"""
                return jsonify(
                    {
                        "success": True,
                        "categories": {
                            category.id: category.type for category in main_category
                        },
                    }
                )

        except:
            abort(404)

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

    @app.route("/questions")
    def get_questions():
        all_questions = Question.query.all()
        try:
            if all_questions is None:
                abort(404)
            else:
                current_questions, all_questions = paginate_questions(
                    request, all_questions
                )
                categories = Category.query.order_by(Category.type).all()
                return jsonify(
                    {
                        "success": True,
                        "questions": current_questions,
                        "total_questions": len(all_questions),
                        "categories": {
                            category.id: category.type for category in categories
                        },
                        "current_category": None,
                    }
                )
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        try:

            question.delete()

            return jsonify({"success": True, "deleted": question_id})

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        # Get json object
        body = request.get_json()
        try:
            new_question = body.get("question")
            new_category = body.get("category")
            new_answer = body.get("answer")
            new_difficulty = body.get("difficulty")

            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )

            question.insert()

            return jsonify({"success": True, "created": question.id})
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search():
        body = request.get_json()
        try:
            search_term = body.get("searchTerm")
            search_query = Question.query.filter(
                Question.question.ilike("%" + search_term + "%")
            ).all()
            if len(search_query) == 0:
                abort(404)
            else:

                return jsonify(
                    {
                        "success": True,
                        "questions": [question.format() for question in search_query],
                        "total_questions": len(search_query),
                        "current_category": None,
                    }
                )

        except:
            abort(404)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    # using collection/item/collection
    @app.route("/categories/<category_id>/questions")
    def get_questions_by_category(category_id):

        try:
            categorized_questions = Question.query.filter(
                Question.category == category_id
            ).all()
            if categorized_questions is None:
                abort(404)
            else:
                return jsonify(
                    {
                        "success": True,
                        "questions": [
                            question.format() for question in categorized_questions
                        ],
                        "total_questions": len(categorized_questions),
                        "current_category": category_id,
                    }
                )
        except:
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

    @app.route("/quizzes", methods=["POST"])
    def play():
        body = request.get_json()
        try:
            # Get previous questions and category to query the database with
            previous_questions = body.get("previous_questions")
            quiz_category = body.get("quiz_category")
            if (previous_questions, quiz_category) is None:
                abort(404)
            available_questions = []
            if quiz_category["id"] == 0:
                questions = Question.query.all()
                # for question in questions:
                #     if question.id not in previous_questions:
                #         available_questions.append(question)
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category["id"]
                ).all()
            # An error occurs if questions in category are not up to 5 so tried to send a message to the frontend that shows that
            for question in questions:
                if question.id not in previous_questions:
                    available_questions.append(question)

            if len(available_questions) < 5:
                return jsonify(
                    {
                        "success": True,
                        "question": random.choice(available_questions).format(),
                        "warning": "Warning: Available questions are not up to 5. You cannot finish the quiz!",
                    }
                )
            else:
                return jsonify(
                    {
                        "success": True,
                        "question": random.choice(available_questions).format(),
                    }
                )
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": 404, "message": "bad request"}), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app
