from fastapi.testclient import TestClient
from app.app import app
import mysql.connector
import pytest


client = TestClient(app)

def test_blog():
    # TestClient handles the URL parameters for you
    response = client.get("/blogs", params={"limit": 5, "offset": 0})
    assert response.status_code == 200
    assert "data" in response.json()

def test_blog_by_id():
    response = client.get("/blogs/1")
    assert response.status_code == 200
    assert response.json() == [1, "this is one", "max ", "des "]

# Mocking db
@pytest.fixture
def mock_db(mocker):
  
    mock_cursor = mocker.patch("app.api.blogs.cursor")
    mock_db_conn = mocker.patch("app.api.blogs.mydb")
    return mock_cursor, mock_db_conn

# Get all blogs
def test_get_blogs(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchall.return_value = [(1,'title1',"author1","contenet1")]
    response = client.get("/blogs")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    # print(mock_cursor.fetchall.called) # You can remove this print statement

# Get by id
def test_get_blogs_by_id(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = [(1,'title1',"author1","contenet1")]
    response = client.get("/blogs/1")
    assert response.status_code == 200
    assert response.json() == [[1,'title1',"author1","contenet1"]]

# Blog not found
def test_blog_not_found(mock_db):
    mock_cursor, _ = mock_db
    mock_cursor.fetchone.return_value = None
    response = client.get("/blogs/999")
    assert response.status_code == 404

# Insert blog
def test_create_blog(mock_db):
    mock_cursor, mock_db_conn = mock_db
    data = {
        "blog_id": 1,
        "title": "Test",
        "author": "Me",
        "Content": "hello"
    }
    response = client.post("/blogs", json=data)
    assert response.status_code == 201
    mock_db_conn.commit.assert_called_once()

# Test for duplicate blog entry (handles the error scenario)
def test_create_duplicate_blog(mock_db):
    mock_cursor, mock_db_conn = mock_db
    data = {
        "blog_id": 1,
        "title": "Duplicate Test",
        "author": "Me",
        "Content": "hello again"
    }

    # Simulate the database raising an IntegrityError when commit() is called
    # (Assuming your app catches this and returns a 409 Conflict)
    # The error code ER_DUP_ENTRY is common for MySQL duplicate key errors.
    mock_db_conn.commit.side_effect = mysql.connector.errors.IntegrityError(
        msg="Duplicate entry '1' for key 'PRIMARY'",
        errno=1062 # MySQL error code for ER_DUP_ENTRY
    )
    
    response = client.post("/blogs", json=data)
    
    # Assert that the application returns a 409 Conflict status code
    assert response.status_code == 409 
    assert "already exists" in response.json().get("detail")
