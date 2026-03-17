from fastapi.testclient import TestClient
from app.app import app  # Explicitly import the FastAPI instance
import pytest
from database.db import cursor
from database.db import mydb
import mysql.connector

client = TestClient(app)

def test_blog():
    # TestClient handles the URL parameters for you
    response = client.get("/blogs", params={"limit": 5, "offset": 0})
    assert response.status_code == 200
    assert "data" in response.json()


def test_blog_by_id():
    response = client.get("/blogs/1")
    assert response.status_code==200
    assert response.json()==[1, "this is one", "max ", "des "]


 #mocking db   

@pytest.fixture
def mock_db(mocker):
    mock_cursor=mocker.patch("app.api.blogs.cursor")
    mock_db=mocker.patch("app.api.blogs.mydb")
    return mock_cursor,mock_db



#get all blogs
def test_get_blogs(mock_db):
    mock_cursor,_ = mock_db

    mock_cursor.fetchall.return_value=[(1,'title1',"author1","contenet1")]
    
    response = client.get("/blogs")
    assert response.status_code==200
    assert len(response.json()["data"])==1

    print(mock_cursor.fetchall.called)


#get by id

def test_get_blogs_by_id(mock_db):
    mock_cursor,_ = mock_db

    mock_cursor.fetchone.return_value=[(1,'title1',"author1","contenet1")]
    
    response = client.get("/blogs/1")
    assert response.status_code==200
    assert response.json()==[[1,'title1',"author1","contenet1"]]


#blog not found 

def test_blog_not_found(mock_db):
    mock_cursor,_ = mock_db
    mock_cursor.fetchone.return_value=None
    response = client.get("/blogs/999")
    assert response.status_code==404



#insert blog 

def test_create_blog(mock_db):
    mock_cursor,mock_db_conn=mock_db
    data = {
        "blog_id":1,
        "title":"Test",
        "author":"Me",
        "Content":"hello"
    }

    response = client.post("/blogs",json=data)
    assert response.status_code==201
    mock_db_conn.commit.assert_called_once()



#duplicate blog
