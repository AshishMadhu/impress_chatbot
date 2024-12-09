
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id == -1:
        return False, "Please use the /reset command to start over."
    if current_question_id:
        current_question = PYTHON_QUESTION_LIST[current_question_id - 1]
        if answer not in current_question["options"]:
            return False, "Invalid answer. Please choose from options."
        elif answer == current_question["answer"]:
            answers = session.get('answers', [])
            answers.append({
                'question_id': current_question_id - 1,
                'answer': answer
            })
            session['answers'] = answers
    return True, ""


def get_question_and_options(question_id):
    question_id = int(question_id)
    question = f'{PYTHON_QUESTION_LIST[question_id]["question_text"]} <br> Options: <br> {"<br> ".join(PYTHON_QUESTION_LIST[question_id]["options"])}'
    return question

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        return get_question_and_options(0), 1
    next_question_id = current_question_id + 1
    if next_question_id <= len(PYTHON_QUESTION_LIST):
        return get_question_and_options(next_question_id - 1), next_question_id
    else:
        return None, -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get('answers', [])
    score = 0
    for answer in answers:
        if answer['answer'] == PYTHON_QUESTION_LIST[answer['question_id']]["answer"]:
            score += 1
    session['answers'] = []
    total_number_of_questions = len(PYTHON_QUESTION_LIST)
    percentage = round((score / total_number_of_questions) * 100)
    if percentage == 100:
        performance = "Excellent!"
    elif percentage >= 80:
        performance = "Great work!"
    elif percentage >= 50:
        performance = "Good job!"
    else:
        performance = "Keep practicing!"
    return f"Your score is {score} out of {total_number_of_questions}, {performance}"
