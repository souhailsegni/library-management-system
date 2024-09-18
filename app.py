from flask import Flask, render_template, request, redirect, url_for,flash
from models import db, User, Book, BorrowedBook
from datetime import datetime
import config

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        new_user = User(name=name, surname=surname, dob=dob)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        new_book = Book(name=name, quantity=quantity)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        book_id = request.form['book_id']
        return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d').date()
        
        # Retrieve the book and check its quantity
        book = Book.query.get(book_id)
        if not book:
            flash('Book not found', 'danger')
            return redirect(url_for('borrow_book'))
        
        if book.quantity <= 0:
            flash('Book is not available', 'danger')
            return redirect(url_for('borrow_book'))

        # Create the BorrowedBook entry
        borrowed_book = BorrowedBook(
            user_name=name,
            user_surname=surname,
            book_id=book_id,
            return_date=return_date
        )

        # Update book quantity
        book.quantity -= 1
    
        # Add to the session and commit
        db.session.add(borrowed_book)
        db.session.commit()
        flash('Book borrowed successfully', 'success')
        return redirect(url_for('index'))
    
    # Pass the list of books to the template
    books = Book.query.all()
    return render_template('borrow_book.html', books=books)

@app.route('/view_books')
def view_books():
    books = Book.query.all()
    return render_template('view_books.html', books=books)

@app.route('/view_history')
def view_history():
    history = BorrowedBook.query.all()
    return render_template('view_history.html', history=history)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
