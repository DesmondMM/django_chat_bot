import json
import random
import re
import os
import requests
from pprint import pprint
from django.shortcuts import render
from django.views import generic


from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


jokes = {
         'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
                    """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""],
         'fat':    ["""Yo' Mama is so fat, when she goes to a restaurant, instead of a menu, she gets an estimate.""",
                    """ Yo' Mama is so fat, when the cops see her on a street corner, they yell, "Hey you guys, break it up!" """],
         'dumb':   ["""Yo' Mama is so dumb, when God was giving out brains, she thought they were milkshakes and asked for extra thick.""",
                    """Yo' Mama is so dumb, she locked her keys inside her motorcycle."""]
         }


class YoMamaBotView(generic.View):
    # The get method is the same as before.. omitted here for brevity
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == os.getenv('FB_VERIFICATION_KEY'):
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        print('my env {}'.format(os.getenv('FB_VERIFICATION_KEY')))
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()


def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', recevied_message).lower().split()
    joke_text = ''
    for token in tokens:
        if token in jokes:
            joke_text = random.choice(jokes[token])
            break
    post_message_url = ''
    if not joke_text:
        joke_text = "I didn't understand! Send 'stupid', 'fat', 'dumb' for a Yo Mama joke!"
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(
            os.getenv('FB_ACCESS_KEY'))
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": joke_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())
