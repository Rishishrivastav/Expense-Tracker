from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user
from app import app, db
from app.models import Transaction
from app.utils import generate_pie_chart

@app.route('/')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    total_income = sum(t.amount for t in transactions if t.type == 'Income')
    total_expense = sum(t.amount for t in transactions if t.type == 'Expense')
    pie_chart = generate_pie_chart(transactions)
    return render_template('dashboard.html', transactions=transactions, income=total_income, expense=total_expense, chart=pie_chart)

@app.route('/add', methods=['POST'])
@login_required
def add_transaction():
    t = Transaction(
        user_id=current_user.id,
        amount=float(request.form['amount']),
        category=request.form['category'],
        date=request.form['date'],
        type=request.form['type'],
        description=request.form['description']
    )
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
@login_required
def delete_transaction(id):
    t = Transaction.query.get(id)
    if t.user_id == current_user.id:
        db.session.delete(t)
        db.session.commit()
    return redirect(url_for('dashboard'))
