import logging
from flask import Flask, jsonify, request
from http import HTTPStatus

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Merged book list
books = [
    {"id": 1, "title": "How to be a professional cook", "author": "Pewdiepie", "year": 2014},
    {"id": 2, "title": "1992", "author": "Mike Tyson", "year": 1966},
]

# Helper function to find a book by ID
def find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)

@app.route("/")
def hello_user():
    return "Hello, User!"


# GET all books
@app.route("/api/books", methods=["GET"])
def get_books():
    return jsonify({"success": True, "data": books, "total": len(books)}), HTTPStatus.OK


# GET a single book by ID
@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND
    return jsonify({"success": True, "data": book}), HTTPStatus.OK


# CREATE a new book
@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    required_fields = ["title", "author", "year"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required fields: {field}"}), HTTPStatus.BAD_REQUEST

    # Validate 'year' field
    if not isinstance(data["year"], int) or data["year"] < 1000 or data["year"] > 2100:
        return jsonify({"success": False, "error": "Invalid year provided"}), HTTPStatus.BAD_REQUEST

    new_book = {
        "id": max(book["id"] for book in books) + 1,
        "title": data["title"],
        "author": data["author"],
        "year": data["year"],
    }

    books.append(new_book)

    # Log the addition of a new book
    logging.info(f"New book added: {new_book}")
    return jsonify({"success": True, "data": new_book}), HTTPStatus.CREATED


# UPDATE a book by ID
@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    if not request.is_json:
        return jsonify({"success": False, "error": "Content-type must be application/json"}), HTTPStatus.BAD_REQUEST

    data = request.get_json()
    allowed_fields = ["title", "author", "year"]
    for field in data:
        if field not in allowed_fields:
            return jsonify({"success": False, "error": f"Invalid field: {field}"}), HTTPStatus.BAD_REQUEST

    book.update(data)

    logging.info(f"Book with id {book_id} updated: {book}")
    return jsonify({"success": True, "data": book}), HTTPStatus.OK


# DELETE a book by ID
@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    books.remove(book)
    logging.info(f"Book with id {book_id} deleted")
    return jsonify({"success": True, "message": f"Book with id {book_id} deleted"}), HTTPStatus.OK


# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), HTTPStatus.NOT_FOUND


# Error handler for 500
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": "Internal Server Error"}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(debug=True)
