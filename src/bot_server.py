import os
from flask import Flask, request
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
import re

from src.conversational_user_interfaces.professional import Professional
from src.parsing.regex_classifier import attempt_to_classify, construct_according_to_classification
from src.security_estimator import calculate_security_risk

app = Flask(__name__)
bot_token = os.environ.get("SLACK_BOT_API_TOKEN")
bot_signature = os.environ.get("SLACK_BOT_SIGNING_SECRET")
if None in [bot_token, bot_signature]:
    raise ValueError("Bot Token and Bot Signing Secret must be set")

client = WebClient(token=bot_token)
bolt_app = App(token=bot_token, signing_secret=bot_signature)
attitude = Professional()


@app.route("/hyper-vyper/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    print("Request received")
    # slack_event = request.json
    # print(slack_event)
    # print(f"recieved event via message: {slack_event['event']['text']}")
    return handler.handle(request)


@bolt_app.message("hello vyper")
def greetings(payload: dict, say: Say):
    """ This will check all the message and pass only those which has 'hello vyper' in it """
    user = payload.get("user")
    say(f"Hi <@{user}>")


@bolt_app.command("/help")
def help_command(say, ack):
    ack()
    text = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "This is a **slash command**"
                }
            }
        ]
    }
    say(text=text)


@bolt_app.command("/classify")
def classify_command(payload, ack):
    ack()
    blocks = [
        attitude.generate_acknowledgement_block(payload),
        attitude.generate_reflection_block(payload),
    ]

    print(payload)
    channel = payload.get('channel_name')
    thread_ts = payload.get('ts')
    user_message = payload.get('text')
    request_type = attempt_to_classify(user_message)
    blocks.append(attitude.generate_initial_classification_block(request_type))

    formed_request = construct_according_to_classification(request_type, user_message)
    security_risk = calculate_security_risk(formed_request)
    print(f"Channel: {channel}\nthread_ts: {thread_ts}")
    print(f"identified_request_type: {request_type}\nfrom user_message: {user_message}")
    print(f"formed request: {formed_request}\nsecurity_risk: {security_risk}")

    if formed_request.is_valid() and security_risk < 75:
        blocks.append(attitude.generate_approval_block(payload))
    else:
        blocks.append(attitude.generate_rejection_block(payload))
    print(blocks)
    client.chat_postMessage(channel=channel,
                            thread_ts=thread_ts,
                            blocks=blocks,
                            text='hyper vyper has processed your request')
    return formed_request


@bolt_app.message(re.compile("(hi|hello|hey) vyper", re.IGNORECASE))
def reply_in_thread(payload: dict):
    """ This will reply in thread instead of creating a new thread """
    response = client.chat_postMessage(channel=payload.get('channel'),
                                       thread_ts=payload.get('ts'),
                                       text=f"Hi<@{payload['user']}>")


handler = SlackRequestHandler(bolt_app)

if __name__ == '__main__':
    # Creating an instance of the Webclient class
    app.run(host='0.0.0.0', port=8080, debug=True)
