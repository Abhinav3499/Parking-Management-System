from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Question

views_blueprint = Blueprint('views', __name__)

# Dashboard for user
@views_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Dashboard for admin to create/set questions
@views_blueprint.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        question_text = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_option = request.form['correct_option']

        new_question = Question(question=question_text, option_a=option_a, option_b=option_b,
                                option_c=option_c, option_d=option_d, correct_option=correct_option)
        db.session.add(new_question)
        db.session.commit()

        flash('Question added successfully!', 'success')

    return render_template('admin_dashboard.html')

# Quiz page for users to attempt
@views_blueprint.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    questions = Question.query.all()

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected_option = request.form.get(f'question_{q.id}')
            if selected_option == q.correct_option:
                score += 1

        flash(f'Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('views.dashboard'))

    return render_template('quiz.html', questions=questions)
