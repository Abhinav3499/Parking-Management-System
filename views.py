from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Subject, Chapter, Quiz, Question

views_blueprint = Blueprint('views', __name__)

# Admin Dashboard
@views_blueprint.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        if 'add_subject' in request.form:
            subject_name = request.form['subject_name']
            new_subject = Subject(name=subject_name)
            db.session.add(new_subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')

        elif 'add_chapter' in request.form:
            chapter_name = request.form['chapter_name']
            subject_id = request.form['subject_id']
            new_chapter = Chapter(name=chapter_name, subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')

        elif 'add_quiz' in request.form:
            quiz_title = request.form['quiz_title']
            duration = request.form['duration']
            chapter_id = request.form['chapter_id']
            new_quiz = Quiz(title=quiz_title, duration=duration, chapter_id=chapter_id)
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')

    subjects = Subject.query.all()
    return render_template('admin_dashboard.html', subjects=subjects)

# User Dashboard
@views_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('user_dashboard.html', user=current_user)

# Quiz Attempt
@views_blueprint.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1
        flash(f'Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('views.dashboard'))

    return render_template('quiz.html', quiz=quiz, questions=questions)