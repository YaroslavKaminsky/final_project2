from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey


class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.id = None
        self.list_of_quizes = []

    def add_quiz(self, quiz):
        if isinstance(quiz, Quiz):
            self.list_of_quizes.append(quiz)
        else:
            raise TypeError('Quiz must be instance of Quiz class.')

    def del_quiz(self, id_):
        for index, quiz in enumerate(self.list_of_quizes):
            if quiz.id == id_:
                del self.list_of_quizes[index]
                break

    def get_user_from_db(self):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        result = list(
            engine.execute(f"select user_id from user where name='{self.name}' and password='{self.password}'"))
        if len(result):
            self.id = result[0][0]
            quiz_list = engine.execute(f'select * from quiz where user_id = {self.id}')
            for row in quiz_list:
                self.add_quiz(Quiz(row[0], row[2]))
            return self
        else:
            msg = 'Wrong user_name or password. Please try again or sign up.'
            return msg

    def get_list_of_quizes(self):
        result = []
        for ele in self.list_of_quizes:
            result.append((int(ele.id), ele.name))
        return result

    @staticmethod
    def number_of_users():
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        result = engine.execute('select user_id from user')
        return len(list(result))

    def add_user_to_db(self):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )
        metadata = MetaData()
        connection = engine.connect()

        id_ = User.number_of_users() + 1
        result = list(engine.execute(f"select user_id from user where name='{self.name}'"))
        if not len(result):
            user_table = Table('user', metadata,
                               Column('user_id', Integer, primary_key=True),
                               Column('name', String(255), nullable=False),
                               Column('password', String(255), nullable=False)
                               )
            insert = user_table.insert().values(
                user_id=id_,
                name=self.name,
                password=self.password
            )
            connection.execute(insert)
            return self
        else:
            msg = f'The user with name {self.name} is already exist. Try other name.'
            return msg

    def convert_to_dict(self):
        id_ = self.id
        name = self.name
        list_of_quizes = self.list_of_quizes
        result = {
            'id': id_,
            'name': name,
            'list_of_quizes': list_of_quizes
        }
        return result

    def __repr__(self):
        return f'ID = {self.id}, name = {self.name}, password = {self.password}'

    def __str__(self):
        return self.__repr__()


class Quiz:
    def __init__(self, id, name):
        self.name = name
        self.id = id
        self.list_of_questions = []

    def add_question(self, question):
        if isinstance(question, Question):
            self.list_of_questions.append(question)
        else:
            raise TypeError('Question must be instance of Question class.')
        # if question is dict:
        #     question = convert_dict_to_question(question)

    def get_from_db(self):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        result = engine.execute(f'select * from question where quiz_id={self.id}')
        for row in result:
            question = Question(row[0], row[2], row[3:len(row) - 1], row[-1])
            self.add_question(question)
        return self

    @classmethod
    def get_by_id(cls, id):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )
        quiz_name = list(
            engine.execute(f'select quiz_name from quiz where quiz_id = {id}')
        )
        result = cls(id, quiz_name[0][0])
        question_table = engine.execute(f'select * from question where quiz_id={id}')
        for row in question_table:
            question = Question(row[0], row[2], row[3:len(row) - 1], row[-1])
            result.add_question(question)
        return result


    @staticmethod
    def number_of_quizes():
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        result = engine.execute('select quiz_id from quiz order by quiz_id')
        result = list(result)
        return result[-1][0]

    @classmethod
    def new_quiz(cls, name):
        id_ = Quiz.number_of_quizes() + 1
        return cls(id_, name)

    def add_to_db(self, user):

        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        self.id = Quiz.number_of_quizes() + 1
        metadata = MetaData()
        connection = engine.connect()
        user_table = Table('quiz', metadata,
                           Column('quiz_id', Integer, primary_key=True),
                           Column('user_id', Integer, ForeignKey('user.user_id'), nullable=False),
                           Column('quiz_name', String(255), nullable=False)
                           )
        insert = user_table.insert().values(
            quiz_id=self.id,
            user_id=user.id,
            quiz_name=self.name
        )
        connection.execute(insert)

        for question in self.list_of_questions:
            question.add_question(self)
        return self

    def edit_quiz(self):
        pass

    def delete_quiz(self):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        engine.execute(f'delete from question where quiz_id={str(self.id)}')
        engine.execute(f'delete from quiz where quiz_id={str(self.id)}')

    def repres(self):
        result = []
        for index, question in enumerate(self.list_of_questions):
            result.append(f'{index+1}. {question.question} Right answer is {question.answers[question.right_answer - 1]}')
        return result

    def convert_to_dict(self):
        id_ = self.id
        name = self.name
        list_of_questions = self.list_of_questions
        result = {
            'id': id_,
            'name': name,
            'list_of_questions': list_of_questions
        }
        return result

    def __repr__(self):
        result_string = f'{self.name}'
        for index, question in enumerate(self.list_of_questions):
            result_string += f'{index + 1}. {question.question} \n ' \
                             f'1.{question.answers[0]}    2.{question.answers[1]}    3.{question.answers[2]}   4.{question.answers[3]} \n ' \
                             f'right_answer is {question.answers[question.right_answer - 1]} \n'
        return result_string

    def __str__(self):
        return self.__repr__()


class Question:
    def __init__(self, id, question, answers, right_answer):
        self.id = id
        self.question = question
        self.answers = answers
        self.right_answer = right_answer

    @staticmethod
    def number_of_questions():
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        result = engine.execute('select question_id from question order by question_id')
        result = list(result)
        return result[-1][0]

    @classmethod
    def new_question(cls, question, answers, right_answer):
        id_ = Question.number_of_questions() + 1
        return cls(id_, question, answers, right_answer)

    def add_question(self, quiz):
        engine = create_engine(
            'mysql+pymysql://root:root27@localhost/quiz2'
        )

        metadata = MetaData()
        connection = engine.connect()
        self.id = Question.number_of_questions() + 1

        msg = 'Your question has been saved'
        question_table = Table('question', metadata,
                               Column('question_id', Integer, primary_key=True),
                               Column('quiz_id', Integer, ForeignKey('quiz.quiz_id'), nullable=False),
                               Column('question_text', String(255), nullable=False),
                               Column('option1', String(255), nullable=False),
                               Column('option2', String(255), nullable=False),
                               Column('option3', String(255), nullable=False),
                               Column('option4', String(255), nullable=False),
                               Column('right_answer', Integer, nullable=False)
                               )
        insert = question_table.insert().values(
            question_id=self.id,
            quiz_id=quiz.id,
            question_text=self.question,
            option1=self.answers[0],
            option2=self.answers[1],
            option3=self.answers[2],
            option4=self.answers[3],
            right_answer=self.right_answer
        )
        connection.execute(insert)
        return self

    def edit_question(self):
        pass

    def delete_question(self):
        pass

    def __repr__(self):
        return convert_to_dict(self)

    def __str__(self):
        return self.__repr__()


def convert_to_dict(question: Question):
    dictionary = dict()
    dictionary['id'] = question.id
    dictionary['question'] = question.question
    dictionary['answers'] = question.answers
    dictionary['right_answer'] = question.right_answer
    return dictionary


def get_list_of_quizes():
    engine = create_engine(
        'mysql+pymysql://root:root27@localhost/quiz2'
    )
    result = engine.execute(f'select * from quiz')
    list_of_quizes = []
    for row in result:
        list_of_quizes.append((row[0], row[-1]))
    return list_of_quizes


if __name__ == '__main__':
    # user = User('admin', 'admin')
    # print(user.get_user_from_db())
    # print(user.list_of_quizes)
    # u = User('admin', 'admin').get_user_from_db()
    # print(u.list_of_quizes)
    # print(u.get_list_of_quizes())
    # Quiz(2, None).delete_quiz()
    print(Question.number_of_questions())