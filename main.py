from piazza_api import Piazza
from markdownify import markdownify
import os

def create_slack_message(piazza_post):
    parent_history = piazza_post['history']
    most_recent_parent_post = parent_history[len(parent_history) - 1]
    message = {
        'response_type': 'in_channel',
        'blocks': [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': most_recent_parent_post['subject'],
                    'emoji': True
                }
            },
            {
                'type': 'divider'
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': markdownify(most_recent_parent_post['content'])
                }
            }
        ]
    }
    return message


def get_link(question_num):
    return os.environ.get('PIAZZA_BASE_URL') + str(question_num)

def get_content(question_num):
    p = Piazza()
    p.user_login(email=os.environ.get('PIAZZA_EMAIL'), password=os.environ.get('PIAZZA_PASSWORD'))
    cs33 = p.network("keslbz8fxy144e")
    post = cs33.get_post(question_num)
    return create_slack_message(post)

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

print(handle_input('get 388'))