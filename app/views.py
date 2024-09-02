from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import Expenses
from .forms import EditExpense
from flask_login import current_user, login_required
from datetime import date

views = Blueprint('views', __name__)

# CREATE
@views.route('/add_expense', methods=['GET', 'POST'])
@login_required
def adding_new_expenses():
    # insert code here
    form = EditExpense(request.form)

    if form.validate_on_submit():
        new_expense = Expenses(
            type=form.type.data,
            description=form.description.data,
            date_purchase=form.date.data,
            amount=form.amount.data,
            user=current_user.email
        )
        db.session.add(new_expense)
        db.session.commit()

        return redirect(url_for("views.show_expenses"))

    return render_template("add_expense.html", form=form)



# READ
@views.route('/expenses')
@login_required
def show_expenses():
    # insert code here
    expenses_user = Expenses.query.filter_by(user=current_user.email).all()

    total_amount = 0
    for expense in expenses_user:
        total_amount += expense.amount

    return render_template("expenses.html", expenses=expenses_user, name_user=current_user.name, total=round(total_amount, 2))


# UPDATE
@views.route('/mod_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def modifying_expenses(expense_id):
    # insert code here
    expense = Expenses.query.filter( Expenses.user==current_user.email,
                               Expenses.expense_id == expense_id).first()
    if not expense:
        flash('You do not have this expense.', category='error')
        return redirect(url_for("views.show_expenses"))

    form = EditExpense(request.form)

    if form.validate_on_submit():
        expense.type = form.type.data
        expense.description = form.description.data
        expense.date_purchase = form.date.data
        expense.amount = form.amount.data
        db.session.commit()

        return redirect(url_for("views.show_expenses"))

    else:
        if request.method == 'GET':
            form = EditExpense(
                data={
                    "type": expense.type,
                    "description": expense.description,
                    "date": date(int(expense.date_purchase[:4]), int(expense.date_purchase[5:7]),
                                    int(expense.date_purchase[8:])),
                    "amount": expense.amount
                }
            )
    return render_template("mod_expense.html", form=form)


# DELETE
@views.route('/del_expense', methods=['POST'])
@login_required
def deleting_expenses():
    # insert code here
    expense = Expenses.query.filter(# Expenses.user == current_user.email,
    Expenses.expense_id == request.form.get("id")).first()
    if expense:
        db.session.delete(expense)
        db.session.commit()

    return redirect(url_for("views.show_expenses"))
