import os
from flask import Flask, request
from slack_sdk import WebClient
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler
from cachetools import TTLCache
import logging

from src.conversational_user_interfaces.professional import Professional
from src.parsing.constants import RequestFollowUp
from src.parsing.regex_classifier import attempt_to_classify, construct_according_to_classification
from src.parsing.requests import UnIdentifiedUserRequest, UserRequest, RequestTypes
from src.security_estimator import calculate_security_risk

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
def handle_message(message: dict, client: WebClient, say: Say, context):
    """
    Handles all incoming messages and checks if they are replies
    to the bot's own messages within a thread.
    """
    logger.info(f"Received message: {message}")

    if is_message_inside_a_thread(message):
        thread_root_ts = message['thread_ts']
        channel_id = message['channel']
        user_id = message['user']  # The user who replied

        logger.info(f"Message is a thread reply. Thread TS: {thread_root_ts}")

        try:
            result = client.conversations_history(
                channel=channel_id,
                latest=thread_root_ts,
                inclusive=True,
                limit=1
            )

            if result['ok'] and result['messages']:
                root_message = result['messages'][0]
                entire_thread = client.conversations_replies(channel=channel_id, ts=thread_root_ts)
                logger.info(f"Root message of thread: {root_message}")


                if 'bot_id' in root_message and root_message['bot_id'] == context.bot_id:
                    logger.info(f"User '{user_id}' replied to our bot's message in thread: '{message['text']}'")

                    say(
                        text=f"Hey <@{user_id}>! Thanks for replying to my previous message in this thread. we were discussing {requests_map[thread_root_ts]}",
                        thread_ts=thread_root_ts  # Ensure the reply goes back into the same thread
                    )
                else:
                    logger.info("Root message was not from this bot.")
            else:
                logger.warning(f"Could not retrieve root message for thread_ts: {thread_root_ts}")

        except Exception as e:
            logger.error(f"Error fetching thread history: {e}")


def is_message_inside_a_thread(payload):
    return 'thread_ts' in payload and payload['thread_ts'] != payload['ts']


@bolt_app.command("/help")
def help_command(say, ack):
    ack()
    text = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I apologize, but you cannot be helped."
                }
            }
        ]
    }
    say(text=text)


@bolt_app.command("/classify")
def classify_command(payload, ack, client):
    """This initiates a conversation about a security request."""
    ack()
    blocks = [
        attitude.generate_acknowledgement_block(payload),
        attitude.generate_reflection_block(payload),
    ]

    logger.debug(payload)
    channel = payload.get('channel_name')
    thread_ts = payload.get('ts')
    user_message = payload.get('text')
    request_type = attempt_to_classify(user_message)
    blocks.append(attitude.generate_initial_classification_block(request_type))

    formed_request = construct_according_to_classification(request_type, user_message)

    logger.debug(f"Channel: {channel}\nthread_ts: {thread_ts}")
    logger.debug(f"identified_request_type: {request_type}\nfrom user_message: {user_message}")
    blocks.append(attitude.generate_user_request_description_block(formed_request))

    decision = decide_on_follow_up(formed_request)
    reply_blocks = formulate_reply_according_to_follow_up(formed_request, decision)
    blocks.extend(reply_blocks)

    try:
        response_data = client.chat_postMessage(channel=channel,
                                thread_ts=thread_ts,
                                blocks=blocks,
                                text='hyper vyper has processed your request')
        new_ts = response_data['ts']
        logger.info(f"New request: {new_ts}")

        manage_cache_according_to_follow_up(formed_request, decision, thread_ts)
    except Exception as e:
        logger.exception(e)
        logger.error(blocks)
        logger.error('failed to respond to user')
    return formed_request


def decide_on_follow_up(formed_request: UserRequest) -> RequestFollowUp:
    security_risk = calculate_security_risk(formed_request)
    logger.info(f"formed request: {formed_request}\nsecurity_risk: {security_risk}")
    if formed_request.is_valid() and security_risk < 75:
        return RequestFollowUp.ACCEPT
    elif not isinstance(formed_request, UnIdentifiedUserRequest) and not formed_request.is_valid():
        return RequestFollowUp.REQUEST_FURTHER_DETAILS
    else:
        return RequestFollowUp.REJECT


def formulate_reply_according_to_follow_up(formed_request: UserRequest, followup: RequestFollowUp) -> list:
    reply_blocks = []
    if followup is RequestFollowUp.ACCEPT:
        reply_blocks.append(attitude.generate_approval_block())
    elif followup is RequestFollowUp.REQUEST_FURTHER_DETAILS:
        missing_fields = formed_request.get_missing_fields()
        reply_blocks.append(attitude.generate_request_for_fields(missing_fields))
    else:
        reply_blocks.append(attitude.generate_rejection_block())

    return reply_blocks

def manage_cache_according_to_follow_up(formed_request: UserRequest, followup: RequestFollowUp, thread_ts: float) -> None:
    if followup in [RequestFollowUp.ACCEPT, RequestFollowUp.REJECT]:
        requests_map.pop(str(thread_ts), None)
    elif followup is RequestFollowUp.REQUEST_FURTHER_DETAILS:
        requests_map[str(thread_ts)] = formed_request
    else:
        logger.error(f"Encountered unknown followup request: {followup}")


handler = SlackRequestHandler(bolt_app)

if __name__ == '__main__':
    # Creating an instance of the Webclient class
    app.run(host='0.0.0.0', port=8080, debug=True)
