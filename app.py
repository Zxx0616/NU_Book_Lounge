from flask import Flask, render_template, request
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",  # Modify your password
        database="nu_book_lounge_db"
    )

# Helper function for pagination
def get_books(cursor, page, per_page):
    offset = (page - 1) * per_page
    cursor.execute("SELECT * FROM books LIMIT %s OFFSET %s", (per_page, offset))
    return cursor.fetchall()

def get_new_books(cursor, page, per_page):
    offset = (page - 1) * per_page
    one_month_ago = datetime.now() - timedelta(days=30)
    cursor.execute("SELECT * FROM books WHERE added_date >= %s ORDER BY added_date DESC LIMIT %s OFFSET %s", 
                   (one_month_ago, per_page, offset))
    return cursor.fetchall()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Pagination settings
    per_page = 6
    page = request.args.get('page', 1, type=int)

    # Search query
    search_query = request.form.get('search_query', '')
    if search_query:
        cursor.execute("SELECT * FROM books WHERE title LIKE %s", ('%' + search_query + '%',))
        books = cursor.fetchall()
        new_books = []
    else:
        books = get_books(cursor, page, per_page)
        new_books = get_new_books(cursor, page, per_page)

    conn.close()

    # Get total number of books for pagination
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()['COUNT(*)']
    conn.close()

    total_pages = (total_books // per_page) + (1 if total_books % per_page else 0)
    
    return render_template("index.html", books=books, new_books=new_books, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(debug=True)
