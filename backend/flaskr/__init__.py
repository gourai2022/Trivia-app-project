import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_que(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    for que in selection:
        question = que.format()

    current_questions = question[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})     ####learn how to set up CORS from https://flask-cors.readthedocs.io/en/latest/
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.all()
        for category in categories:
            return jsonify({
                        "id" : category.id,
                        "type": category.type,
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
    @app.route("/questions")
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_que(request, selection)
            categories = {}
            
            if len(current_questions) != 0:
                all_categories = Category.query.all()
                for category in all_categories:
                    categories = categories.append(category)

                for que in selection:
                    current_category = Category.query.get(que.category).type
                    return jsonify({
                            "questions": [{
                                "id": Question.query.get(que.category).id,
                                "question": Question.query.get(que.category).question,
                                "answer": Question.query.get(que.category).answer,
                                "difficulty": Question.query.get(que.category).difficulty,
                                "category": que.category
                            }],
                            "totalQuestions": len(selection),
                            "categories": { que.category : categories },
                            "currentCategory": current_category
                            })
        except Exception as e:
            print(f'Exception "{e}" in retrieve_questions()')
            abort(400)                     
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is not None:
                question.delete()
                return jsonify({
                    "success": True,
                    "deleted Question id": question_id,
                    "deleted Question": Question.query.get(question_id).question
                    }
                )

        except Exception as e:
            print(f'Exception "{e}" in delete_question()')
            abort(404)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/question", methods=["POST"])
    def create_question():
        question = Question()
        body = request.get_json()

        question.new_question = body.get("question", None)
        question.new_answer = body.get("answer", None)
        question.new_category = body.get("category", None)
        question.new_difficulty = body.get("difficulty", None)
        #search = body.get("search", None)
        try:
            question.insert()

            return jsonify({
                    "success": True,
                    "question": question.new_question,
                    "total_question": len(Question.query.all()),
                })


        except Exception as e:
            print(f'Exception "{e}" in create_question()')
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
    @app.route("/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search = body.get("search", None)
        try:
            if search:
                que_selection = Question.query.order_by(Question.id).filter(Question.title.ilike("%{}%".format(search)))
                if que_selection:
                    questions = paginate_que(request, que_selection)
                    for que in questions:
                        current_category = Category.query.get(que.category).type
                        return jsonify({
                                "questions": [{
                                    "id": que.id,
                                    "question": que.question,
                                    "answer": que.answer,
                                    "difficulty": que.difficulty,
                                    "category": que.category
                                }],
                                "totalQuestions": len(que_selection),
                                "currentCategory": current_category
                                })
          
        except Exception as e:
            print(f'Exception "{e}" in search_question()')
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def sort_questions_by_categories(cat_id):
        questions = Question.query.filter_by(Question.category == cat_id).all()
        try:
            if questions:
                for que in questions:
                    return jsonify({
                            "questions": [{
                                "id": Question.query.get(que.category).id,
                                "question": Question.query.get(que.category).question,
                                "answer": Question.query.get(que.category).answer,
                                "difficulty": Question.query.get(que.category).difficulty,
                                "category": que.category
                            }],
                            "totalQuestions": len(Question.query.all()),
                            "currentCategory": Category.query.get(cat_id).type
                            })
        except Exception as e:
            print(f'Exception "{e}" in sort_questions_by_categories()')
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
    @app.route("/quizzes", Methods=["POST"])
    def questions_quizzes():
        body = request.get_json()
        category = body.get("quiz_category", None)
        question = body.get("previous_questions", None)
        list_previous_que_id = {}
        try:
            if category is not None:
                quizze_question = Question.query.filter_by(Question.category == category["id"]).all()
                random_no = random.randint(1, len(quizze_question))
                while quizze_question[random_no] is not question["id"]:
                    list_previous_que_id = list_previous_que_id.append(random_no)
                    return jsonify({
                        "previous_questions": list_previous_que_id,
                        "quiz_category": category["id"],
                        "question": [{
                            "id": quizze_question[random_no],
                            "question": Question.query.get(Question.id == quizze_question[random_no]).question,
                            "answer" : Question.query.get(Question.id == quizze_question[random_no]).answer,
                            "difficulty" : Question.query.get(Question.id == quizze_question[random_no]).difficulty,
                            "category" : Question.query.get(Question.id == quizze_question[random_no]).category
                        }]
                    })
        except Exception as e:
            print(f'Exception "{e}" in questions_quizzes()')
            abort(422)
    
    
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    ############################error handlers#######################################

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}), 
            400,
        )

    @app.errorhandler(404)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Page not found"}), 
            404,
        )
    
    @app.errorhandler(405)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Invalid method"}), 
            405,
        )

    @app.errorhandler(422)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable recource"}), 
            422,
        )

    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Internal server error"}), 
            500,
        )    

    return app

