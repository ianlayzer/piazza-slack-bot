from piazza_api import Piazza
from markdownify import markdownify
import os
import json

DIVIDER_BLOCK = {
    'type': 'divider'
}

def create_answer_blocks(response):
    response_type = ''
    if response['type'] == 'i_answer':
        response_type = '*Instructor Answer*'
    elif response['type'] == 's_answer':
        response_type = 'Student Answer*'
    elif response['type'] == 'followup':
        response_type = '*Followup*'
    elif response['type'] == 'feedback':
        response_type = '*Feedback*'

    text_to_display = ''
    if 'history' in response:
        text_to_display = response['history'][0]['content']
    else:
        text_to_display = response['subject']

    blocks = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': response_type
            }
        },
        DIVIDER_BLOCK,
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': markdownify(text_to_display)
            }
        },
        DIVIDER_BLOCK
    ]
    if 'children' in response:
        for child in response['children']:
            blocks += create_answer_blocks(child)
    return blocks

def create_slack_message(piazza_post, question_num):
    most_recent_parent_post = piazza_post['history'][0]

    blocks = [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': str(question_num) + ': ' + most_recent_parent_post['subject']
            }
        },
        DIVIDER_BLOCK,
        {
            'type': 'section',
            'text': {
                'type': 'plain_text',
                'text': 'Posted ' + most_recent_parent_post['created']
            }
        },
        DIVIDER_BLOCK,
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': markdownify(most_recent_parent_post['content'])
            }
        },
        DIVIDER_BLOCK
    ]
    for child in piazza_post['children']:
        blocks += create_answer_blocks(child)

    message = {
        'response_type': 'in_channel',
        'blocks': blocks
    }
    return message


def get_link(question_num):
    return os.environ.get('PIAZZA_BASE_URL') + str(question_num)

def get_content(question_num):
    p = Piazza()
    p.user_login(email=os.environ.get('PIAZZA_EMAIL'), password=os.environ.get('PIAZZA_PASSWORD'))
    cs33 = p.network("keslbz8fxy144e")
    post = cs33.get_post(question_num)
    return create_slack_message(post, question_num)

def handle_input(input):
    tokens = input.split()
    if len(tokens) != 2:
        return "Incorrect number of arguments."
    elif tokens[0] == "link":
        return get_link(int(tokens[1]))
    elif tokens[0] == "get":
        return get_content(int(tokens[1]))
    else:
        return "Unknown command."
def piazza_bot(request):
    return handle_input(request.form['text'])

print(json.dumps(handle_input('get 4416'), indent=2))