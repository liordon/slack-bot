import logging
import os

from cachetools import TTLCache
from flask import Flask, request
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient

from src.bot_policy import handle_message, help_command, classify_and_respond
from src.conversational_user_interfaces.professional import Professional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot_token = os.environ.get("SLACK_BOT_API_TOKEN")
bot_signature = os.environ.get("SLACK_BOT_SIGNING_SECRET")
if None in [bot_token, bot_signature]:
    raise ValueError("Bot Token and Bot Signing Secret must be set")

bolt_app = App(token=bot_token, signing_secret=bot_signature)
attitude = Professional()

requests_map = TTLCache(maxsize=100, ttl=3600)


@app.route("/hyper-vyper/events", methods=["POST"])
def slack_events():
    """ Declaring the route where slack will post a request """
    logger.info("Request received")
    # slack_event = request.json
    # logger.info(slack_event)
    # logger.info(f"recieved event via message: {slack_event['event']['text']}")
    return handler.handle(request)


@bolt_app.message()
def forward_message_to_handler(message: dict, client: WebClient, say: Say, context):
    """
    Handles all incoming messages and checks if they are replies
    to the bot's own messages within a thread.
    """
    handle_message(message, client, say, context)


@bolt_app.command("/help")
def display_help(say, ack):
    ack()
    help_command(say)


@bolt_app.command("/classify")
def forward_command_to_classification(payload, ack, client):
    """This initiates a conversation about a security request."""
    ack()
    classify_and_respond(payload, client)


handler = SlackRequestHandler(bolt_app)

if __name__ == '__main__':
    # Creating an instance of the Webclient class
    app.run(host='0.0.0.0', port=8080, debug=True)
