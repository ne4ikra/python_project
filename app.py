from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель данных
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Доход/Расход
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.amount}>'

# Создание базы данных
with app.app_context():
    db.create_all()

# Маршруты
@app.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    total_income = sum(t.amount for t in transactions if t.category == 'income')
    total_expense = sum(t.amount for t in transactions if t.category == 'expense')
    balance = total_income - total_expense
    return render_template('index.html',
                         transactions=transactions,
                         total_income=total_income,
                         total_expense=total_expense,
                         balance=balance)

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        category = request.form['category']

        transaction = Transaction(amount=amount, description=description, category=category)
        db.session.add(transaction)
        db.session.commit()
        flash('Транзакция успешно добавлена!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Транзакция удалена!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)



