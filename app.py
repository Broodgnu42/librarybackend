from flask import Flask, request, jsonify, send_file
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all domains by default

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            published_year INTEGER,
            location TEXT,
            kstatus TEXT,
            krates REAL,
            jstatus TEXT,
            jrates REAL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Routes
@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return jsonify([dict(book) for book in books])

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    conn.close()
    if book:
        return jsonify({
            'title': book['title'],
            'author': book['author'],
            'genre': book['genre'],
            'published_year': book['published_year'],
            'location': book['location'],
            'kstatus': book['kstatus'],
            'krates': book['krates'],
            'jstatus': book['jstatus'],
            'jrates': book['jrates'],
            'notes': book['notes']
        })
    else:
        return jsonify({'message': 'Book not found'}), 404


@app.route('/books', methods=['POST', 'OPTIONS'])
def add_book():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'  # Or specify a domain
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method == 'POST':
        data = request.json
        print('Received data:', data)
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO books (title, author, genre, published_year, location, kstatus, krates, jstatus, jrates, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (data['title'], data['author'], data.get('genre'), data.get('published_year'), data.get('location'), data.get('kstatus'), data.get('krates'), data.get('jstatus'), data.get('jrates'), data.get('notes'))
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Book added successfully'}), 201

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.json
    conn = get_db_connection()
    conn.execute(
        'UPDATE books SET title = ?, author = ?, genre = ?, published_year = ?, location = ?, kstatus = ?, krates = ?, jstatus = ?, jrates = ?, notes = ? WHERE id = ?',
        (data['title'], data['author'], data.get('genre'), data.get('published_year'), data.get('location'), data.get('kstatus'), data.get('krates'), data.get('jstatus'), data.get('jrates'), data.get('notes'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book updated successfully!'})

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Book deleted successfully!'})
    
@app.route('/download-db')
def download_db():
    return send_file('library.db', as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
