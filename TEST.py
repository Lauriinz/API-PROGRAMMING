import pytest
from TEST_2 import app, db, Book


@pytest.fixture
def test_client():
    """Setup in-memory database and populate with initial test data."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Populate the database with initial test data
            initial_books = [
                Book(title="How to be a professional cook", author="Pewdiepie", year=2014),
                Book(title="Apples and trees", author="Michael B. Jordan", year=1989)
            ]
            db.session.add_all(initial_books)
            db.session.commit()
        yield client


def test_get_book_by_id(test_client):
    """Test retrieving a book by its ID."""
    # Test retrieving an existing book
    response = test_client.get("/api/books/2")
    assert response.status_code == 200
    book_data = response.get_json()
    assert book_data["success"] is True
    assert book_data["data"]["title"] == "Apples and trees"

    # Test retrieving a non-existent book
    response = test_client.get("/api/books/999")
    assert response.status_code == 404
    error_data = response.get_json()
    assert error_data["success"] is False
    assert error_data["error"] == "Book not found"


def test_add_new_book(test_client):
    """Test creating a new book record."""
    new_book_data = {
        "title": "SMD PALAWAN: A Journey to the South",
        "author": "Chris Arinas",
        "year": 2025
    }
    response = test_client.post("/api/books", json=new_book_data)
    assert response.status_code == 201
    created_book = response.get_json()
    assert created_book["success"] is True
    assert created_book["data"]["title"] == "SMD PALAWAN: A Journey to the South"
    
    # Check that the book was actually added to the database
    new_book = Book.query.filter_by(title="SMD PALAWAN: A Journey to the South").first()
    assert new_book is not None
    assert new_book.author == "Chris Arinas"
    assert new_book.year == 2025


def test_create_book_with_missing_fields(test_client):
    """Test error handling for creating a book with missing fields."""
    incomplete_data = {"title": "Incomplete"}
    response = test_client.post("/api/books", json=incomplete_data)
    assert response.status_code == 400
    error_data = response.get_json()
    assert error_data["success"] is False
    assert "Missing required field" in error_data["error"]


def test_update_existing_book(test_client):
    """Test updating a book record."""
    update_data = {"title": "Updated Title", "year": 2023}
    
    # Test updating an existing book
    response = test_client.put("/api/books/1", json=update_data)
    assert response.status_code == 200
    updated_book = response.get_json()
    assert updated_book["success"] is True
    assert updated_book["data"]["title"] == "Updated Title"
    assert updated_book["data"]["year"] == 2023

    # Verify that other fields (e.g., author) remain unchanged
    original_book = Book.query.get(1)
    assert original_book.author == "Pewdiepie"  # Assuming this is the original author

    # Test updating a non-existent book
    response = test_client.put("/api/books/999", json=update_data)
    assert response.status_code == 404
    error_data = response.get_json()
    assert error_data["success"] is False
    assert error_data["error"] == "Book not found"


def test_delete_existing_book(test_client):
    """Test deleting a book by ID."""
    # Test deleting an existing book
    response = test_client.delete("/api/books/1")
    assert response.status_code == 200
    deletion_message = response.get_json()
    assert deletion_message["success"] is True
    assert deletion_message["message"] == "Book with id 1 deleted"
    
    # Verify the book has been deleted from the database
    deleted_book = Book.query.get(1)
    assert deleted_book is None

    # Test deleting a non-existent book
    response = test_client.delete("/api/books/999")
    assert response.status_code == 404
    error_data = response.get_json()
    assert error_data["success"] is False
    assert error_data["error"] == "Book not found"


def test_nonexistent_route(test_client):
    """Test handling requests to non-existent routes."""
    response = test_client.get("/invalid-endpoint")
    assert response.status_code == 404
    error_data = response.get_json()
    assert error_data["success"] is False
    assert error_data["error"] == "Resource not found"
