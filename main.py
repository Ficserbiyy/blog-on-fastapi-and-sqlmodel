from fastapi import FastAPI
from pydantic import BaseModel, ValidationError
from fastapi.responses import HTMLResponse
from typing import Final
import json
import sqlite3

app: Final = FastAPI()

class Post(BaseModel):
    author: str
    title: str
    content: str
    date_posted: str
    
    


class PostsBD:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                title TEXT,
                content TEXT,
                date TEXT
            )
        ''')
        self.conn.commit()


    def add_post(self, author, title, content, date):
        self.cursor.execute(
            "INSERT INTO posts (author, title, content, date) VALUES (?, ?, ?, ?)",
            (author, title, content, date)
        )
        self.conn.commit()
        return self.cursor.lastrowid  # returns created post's id

    def get_all_posts(self):
        self.cursor.execute("SELECT id, author, title, content, date FROM posts")
        return self.cursor.fetchall()

    def get_post(self, post_id):
        self.cursor.execute("SELECT id, author, title, content, date FROM posts WHERE id = ?", (post_id,))
        return self.cursor.fetchone() # Returns tuple or None
    
    def remove_post(self, post_id):
        self.cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        self.conn.commit()




db: Final = PostsBD('Allposts.db')






@app.get("/posts")  # Getting all posts
def get_posts():
    raw_posts = db.get_all_posts()
    # List[tuple] into List[dict]
    formatted_posts = []
    for row in raw_posts:
        formatted_posts.append({
            "id": row[0],
            "author": row[1],
            "title": row[2],
            "content": row[3],
            "date_posted": row[4]
        })
    return formatted_posts


@app.post("/posts") # Posting
def create_post(post: Post):
    # adding to our Database
    new_id = db.add_post(post.author, post.title, post.content, post.date_posted)
    
    # returning response for client
    return {
        "id": new_id, 
        "author": post.author, 
        "title": post.title, 
        "content": post.content, 
        "date_posted": post.date_posted
    }


@app.delete("/posts/{post_id}") # Deleting the post
def delete_post(post_id: int):
    # Checking if there is a post
    existing_post = db.get_post(post_id)
    if not existing_post:
        return {"error": "Post not found"}
        
    db.remove_post(post_id)
    return {"message": f"Post {post_id} succesfully deleted"}

