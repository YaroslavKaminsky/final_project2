from flask import Flask, render_template, redirect, request, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
from quiz import *


app = Flask(__name__)
# application = app

app.config['SECRET_KEY'] = 'Yaroslav'
Bootstrap(app)

user_test = User(None, None)
quiz_test = Quiz(0, None)


class IndexForm(FlaskForm):
    user_name = StringField('User name')
    password = PasswordField('Password')
    log_in = SubmitField('Log in')
    sign_up = SubmitField('Sign up')


class SignupForm(FlaskForm):
    user_name = StringField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    sign_up = SubmitField('Sign up')


class MainForm(FlaskForm):
    quiz_name = SelectField('Choose quiz', choices=get_list_of_quizes())
    my_quiz = SubmitField('My quizzes')
    single_game = SubmitField('Single game')
    multi_game = SubmitField('Multiplayer game')
    log_out = SubmitField('Log out')

    def logging_out(self):
        global user_test, quiz_test
        user_test = User(None, None)
        quiz_test = Quiz(0, None)
        session['counter'] = 0
        session['counter_right'] = []


class UserForm(FlaskForm):
    quiz_name = SelectField('Choose quiz', choices=[])
    create_quiz = SubmitField('Create quiz')
    edit_quiz = SubmitField('Edit quiz')
    delete_quiz = SubmitField('Delete quiz')
    main_page = SubmitField('Main page')
    log_out = SubmitField('Log out')

    def logging_out(self):
        global user_test, quiz_test
        user_test = User(None, None)
        quiz_test = Quiz(0, None)
        session['counter'] = 0
        session['counter_right'] = 0


class TestForm(FlaskForm):
    option_1 = SubmitField('1')
    option_2 = SubmitField('2')
    option_3 = SubmitField('3')
    option_4 = SubmitField('4')


class QuestionForm(FlaskForm):
    quiz_title = StringField('Enter quiz title', validators=[DataRequired()])
    question = StringField('Enter your question', validators=[DataRequired()])
    answer1 = StringField('First Option', validators=[DataRequired()])
    answer2 = StringField('Second Option', validators=[DataRequired()])
    answer3 = StringField('Third Option', validators=[DataRequired()])
    answer4 = StringField('Fourth Option', validators=[DataRequired()])
    right_answer = SelectField('Choose right answer', choices=[(1, 'First Option'), (2, 'Second Option'), (3, 'Third Option'), (4, 'Fourth Option')])
    next_question = SubmitField('Next Question')
    finish_creation = SubmitField('Finish')

    def get_question_from_form(self):
        global quiz_test
        quiz_name = self.quiz_title.data
        quest = self.question.data
        self.question.data = ''
        answers = [self.answer1.data, self.answer2.data, self.answer3.data, self.answer4.data]
        self.answer1.data, self.answer2.data, self.answer3.data, self.answer4.data = '', '', '', ''
        right_answer = int(self.right_answer.data)
        # sessions['quiz'] = Quiz(0, quiz_name)
        quiz_test.name = quiz_name
        quiz_test.add_question(Question(0, quest, answers, right_answer))


class ResultForm(FlaskForm):
    main_page = SubmitField('Main page')


@app.route('/', methods=['GET', 'POST'])
def index():
    global user_test
    session['counter'] = 0
    session['counter_right'] = 0
    msg = ''
    index_form = IndexForm()
    if index_form.validate_on_submit():
        if 'log_in' in request.form:
            name = index_form.user_name.data.lower()
            password = index_form.password.data
            attempt = User(name, password).get_user_from_db()
            if isinstance(attempt, User):
                user_test = attempt
                return redirect('/main')
            else:
                msg = attempt
        elif 'sign_up' in request.form:
            return redirect('/sign_up')
    return render_template('index.html', index_form=index_form, msg=msg)


@app.route('/sign_up', methods=['GET', 'POST'])
def signup():
    msg = ''
    print(user_test, user_test.get_list_of_quizes())
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        name = signup_form.user_name.data.lower()
        password = signup_form.password.data
        new_user = User(name, password).add_user_to_db()
        if isinstance(new_user, User):
            flash('Your account has been created')
            return redirect('/')
        else:
            msg = new_user
    return render_template('sign_up.html', signup_form=signup_form, msg=msg)


@app.route('/main', methods=['GET', 'POST'])
def main():
    global user_test, quiz_test
    print(user_test, user_test.get_list_of_quizes())
    main_form = MainForm()
    if main_form.validate_on_submit():
        if 'my_quiz' in request.form:
            UserForm.quiz_name = SelectField('Choose quiz', choices=user_test.get_list_of_quizes())
            return redirect('/user')
        elif 'single_game' in request.form:
            id_ = main_form.quiz_name.data
            quiz_test = Quiz.get_by_id(id_)
            return redirect('/single_game')
        elif 'multi_game' in request.form:
            id_ = main_form.quiz_name.data
            quiz_test = Quiz.get_by_id(id_)
            return redirect('/multi_game')
        elif 'log_out' in request.form:
            main_form.logging_out()
            return redirect('/')
    return render_template('main.html', main_form=main_form, name=user_test.name)


@app.route('/user', methods=['GET', 'POST'])
def user():
    global user_test, quiz_test
    print(user_test, user_test.get_list_of_quizes())
    msg = ''
    user_form = UserForm()
    # if user_form.validate_on_submit():
    if 'create_quiz' in request.form:
        return redirect('/create_quiz')
    elif 'edit_quiz' in request.form:
        id_ = user_form.quiz_name.data
        quiz_test = Quiz.get_by_id(id_)
        return redirect('/edit_quiz')
    elif 'delete_quiz' in request.form:
        print(dict(request.form))
        id_ = int(user_form.quiz_name.data)
        Quiz(id_, None).delete_quiz()
        user_test.del_quiz(id_)
        UserForm.quiz_name = SelectField('Choose quiz', choices=user_test.get_list_of_quizes())
        msg = 'Quiz was deleted'
    elif 'main_page' in request.form:
        MainForm.quiz_name = SelectField('Choose quiz', choices=get_list_of_quizes())
        return redirect('/main')
    elif 'log_out' in request.form:
        user_form.logging_out()
        return redirect('/')
    return render_template('user.html', user_form=user_form, name=user_test.name, msg=msg)


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    global quiz_test, user_test
    task = QuestionForm()
    if task.validate_on_submit():
        if 'next_question' in request.form:
            task.get_question_from_form()
            session['counter'] += 1
        elif 'finish_creation' in request.form:
            task.get_question_from_form()
            quiz_test.add_to_db(user_test)
            print(quiz_test)
            temp = quiz_test
            user_test.add_quiz(temp)
            quiz_test = Quiz(0, None)
            session['counter'] = 0
            UserForm.quiz_name = SelectField('Choose quiz', choices=user_test.get_list_of_quizes())
            return redirect('/user')
    return render_template('create_quiz.html', task=task, counter=session['counter']+1)


@app.route('/single_game', methods=['GET', 'POST'])
def single_game():
    global quiz_test
    test_ = TestForm()
    name = quiz_test.name
    number_of_questions = len(quiz_test.list_of_questions)
    question = quiz_test.list_of_questions[session['counter']]
    if test_.validate_on_submit():
        if session['counter'] + 1 == number_of_questions:
            if 'option_1' in request.form:
                if question.right_answer == 1:
                    session['counter_right'] += 1
            elif 'option_2' in request.form:
                if question.right_answer == 2:
                    session['counter_right'] += 1
            elif 'option_3' in request.form:
                if question.right_answer == 3:
                    session['counter_right'] += 1
            elif 'option_4' in request.form:
                if question.right_answer == 4:
                    session['counter_right'] += 1
            print(f'Your score {session["counter_right"]} out of {number_of_questions}')
            return redirect('/result')
            # session['counter'], session['counter_right'] = 0, 0
            # quiz_test = Quiz(0, None)
        else:
            if 'option_1' in request.form:
                if question.right_answer == 1:
                    session['counter_right'] += 1
            elif 'option_2' in request.form:
                if question.right_answer == 2:
                    session['counter_right'] += 1
            elif 'option_3' in request.form:
                if question.right_answer == 3:
                    session['counter_right'] += 1
            elif 'option_4' in request.form:
                if question.right_answer == 4:
                    session['counter_right'] += 1
            session['counter'] += 1
            question = quiz_test.list_of_questions[session['counter']]
    return render_template('single_game.html', test_=test_, counter=session['counter'], question=question, name=name)


@app.route('/result', methods=['GET', 'POST'])
def result():
    global quiz_test
    result_form = ResultForm()
    msg = f'Your score {session["counter_right"]} out of {session["counter_right"] + 1}'
    if 'main_page' in request.form:
        session['counter'], session['counter_right'] = 0, 0
        quiz_test = Quiz(0, None)
        return redirect('/main')
    return render_template('result.html', result_form=result_form, msg=msg, quiz=quiz_test.repres())


if __name__ == '__main__':
    app.run(debug=True)
