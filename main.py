from piazza_api import Piazza
import os

def get_link(question_num):
    return os.environ.get('PIAZZA_BASE_URL') + str(question_num)

def get_content(question_num):
    p = Piazza()
    p.user_login(email=os.environ.get('PIAZZA_EMAIL'), password=os.environ.get('PIAZZA_PASSWORD'))
    cs33 = p.network("keslbz8fxy144e")
    post = cs33.get_post(question_num)
    content = post['history'][0]['content']
    return content

def handle_input(input):
    tokens = input.split()
    if len(tokens) != 2:
        return "Incorrect number of arguments."
    elif tokens[0] == "link":
        return get_link(int(tokens[1]))
    elif tokens[0] == "get":
        return get_content(int(tokens[1]))
    
def piazza_bot(request):
    return handle_input(request.form['text'])