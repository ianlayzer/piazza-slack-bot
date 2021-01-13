from piazza_api import Piazza
from markdownify import markdownify
import os
import json

DIVIDER_BLOCK = {
    'type': 'divider'
}

class PiazzaBot:
    def __init__(self):
        self.piazza = Piazza()
        self.piazza.user_login(email=os.environ.get('PIAZZA_EMAIL'), password=os.environ.get('PIAZZA_PASSWORD'))
        self.course = self.piazza.network(os.environ.get('PIAZZA_CLASS_ID'))
        self.question_num = None
        self.post = None
        self.user_map = {}

    def handle_input(self, input):
        tokens = input.split()
        if len(tokens) != 2:
            return "Incorrect number of arguments."
        self.question_num = int(tokens[1])
        if tokens[0] == "link":
            return self.make_link()
        elif tokens[0] == "get":
            return self.get_content()
        else:
            return "Unknown command."

    def make_link(self):
        return 'https://piazza.com/class/' + os.environ.get('PIAZZA_CLASS_ID') + '?cid=' + str(self.question_num)

    def get_content(self):
        self.post = self.course.get_post(self.question_num)
        self.user_map = self.get_users(self.post)
        return self.create_slack_message(self.post)

    def create_slack_message(self, post):
        most_recent_parent_post = post['history'][0]
        asker = self.user_map[most_recent_parent_post['uid']]

        blocks = [
            {
                'type': 'header',
                'text': {
                    'type': 'plain_text',
                    'text': str(self.question_num) + ': ' + most_recent_parent_post['subject']
                }
            },
            DIVIDER_BLOCK,
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': 'Posted by ' + asker['name'] + ' at ' + most_recent_parent_post['created']
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
        for child in post['children']:
            blocks += self.create_answer_blocks(child)

        message = {
            'blocks': blocks
        }
        return message

    def create_answer_blocks(self, response):
        response_type = ''
        if response['type'] == 'i_answer':
            response_type = '*Instructor Answer*'
        elif response['type'] == 's_answer':
            response_type = 'Student Answer*'
        elif response['type'] == 'followup':
            response_type = '*Followup*'
        elif response['type'] == 'feedback':
            response_type = '*Feedback*'


        response_metadata = response['history'][0] if 'history' in response else response
        html_content = response_metadata['content'] if 'content' in response_metadata else response_metadata['subject']
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
                    'text': 'Posted by ' + self.user_map[response_metadata['uid']]['name'] + ' at ' + response_metadata['created']
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': markdownify(html_content)
                }
            },
            DIVIDER_BLOCK
        ]
        if 'children' in response:
            for child in response['children']:
                blocks += self.create_answer_blocks(child)
        return blocks
    
    def get_users(self, post):
        user_id_set = self.get_user_id_set(post, set())
        users = self.course.get_users(list(user_id_set))
        user_map = {}
        for user in users:
            user_map[user['id']] = user
        return user_map

    def get_user_id_set(self, post, user_id_set):
        if 'uid' in post:
            user_id_set.add(post['uid'])
        elif 'history' in post:
            user_id_set.add(post['history'][0]['uid'])
        if 'children' in post:
            for child in post['children']:
                self.get_user_id_set(child, user_id_set)
        return user_id_set

def piazza_bot(request):
    bot = PiazzaBot()
    return bot.handle_input(request.form['text'])

bot = PiazzaBot()
print(json.dumps(bot.handle_input('get 4416'), indent=2))