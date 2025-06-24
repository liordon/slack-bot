import logging

from cachetools import TTLCache
from slack_bolt import Say
from slack_sdk import WebClient

from src.conversational_user_interfaces.professional import Professional
from src.parsing.constants import RequestFollowUp
from src.parsing.regex_classifier import attempt_to_classify, construct_according_to_classification
from src.parsing.requests import UnIdentifiedUserRequest, UserRequest
from src.security_estimator import calculate_security_risk

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

requests_map = TTLCache(maxsize=100, ttl=3600)
attitude = Professional()


def handle_message(message: dict, client: WebClient, say: Say, context):
    """
    Handles all incoming messages and checks if they are replies
    to the bot's own messages within a thread.
    """
    logger.info(f"Received message: {message}")
    thread_request = None
    followup = RequestFollowUp.IRRELEVANT

    if __is_message_inside_a_thread(message):
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
                if __we_initiated_this_thread(context, root_message):
                    logger.info(
                        f"User '{user_id}' replied to our bot's message in thread: '{message['text']}'"
                        )
                    thread_request = requests_map.get(str(thread_root_ts), None)
                    followup = _decide_on_follow_up(thread_request)

                    blocks = [
                        attitude.generate_acknowledgement_block(message),
                        attitude.generate_reflection_block(message),
                    ]

                    if thread_request is not None:
                        completing_request = construct_according_to_classification(
                            thread_request.request_type, message['text']
                            )

                        blocks.append(
                            attitude.generate_user_request_description_block(thread_request)
                            )
                        say(
                            text=f"Hey <@{user_id}>! Thanks for replying to my previous message in this thread. we were discussing {thread_request}",
                            thread_ts=thread_root_ts
                            # Ensure the reply goes back into the same thread
                        )
                    else:
                        say(
                            text=f"Hey <@{user_id}>! I'm sorry, but I closed the request in this thread due to timeout or completion. let's start over.",
                            thread_ts=thread_root_ts
                            # Ensure the reply goes back into the same thread
                        )
                else:
                    logger.info("Root message was not from this bot.")
            else:
                logger.warning(f"Could not retrieve root message for thread_ts: {thread_root_ts}")

        except Exception as e:
            logger.error(f"Error fetching thread history: {e}")

    return thread_request, followup


def __we_initiated_this_thread(context, root_message):
    """compares our bot's ID to the ID of whoever initiated this thread to verify that it's indeed us."""
    return 'bot_id' in root_message and root_message['bot_id'] == context.bot_id


def __is_message_inside_a_thread(payload):
    """compares the thread_ts and ts fields of the message to determine whether it's inside an existing thread."""
    return 'thread_ts' in payload and payload['thread_ts'] != payload['ts']


def help_command(say):
    """returns the help output to the user"""
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


def classify_and_respond(payload, client):
    """This initiates a conversation about a security request."""
    blocks = [
        attitude.generate_acknowledgement_block(payload),
        attitude.generate_reflection_block(payload),
    ]
    new_ts = None

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

    followup = _decide_on_follow_up(formed_request)
    reply_blocks = _formulate_reply_according_to_follow_up(formed_request, followup)
    blocks.extend(reply_blocks)

    try:
        response_data = client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=blocks,
            text='hyper vyper has processed your request'
            )
        new_ts = response_data['ts']
        logger.info(f"New request: {new_ts}")

        _manage_cache_according_to_follow_up(formed_request, followup, new_ts)
    except Exception as e:
        logger.exception(e)
        logger.error(blocks)
        logger.error('failed to respond to user')
    return formed_request, blocks, new_ts


def _decide_on_follow_up(formed_request: UserRequest) -> RequestFollowUp:
    """given a (possibly partial) request parsed from the user, decides what to do with it."""
    security_risk = calculate_security_risk(formed_request)
    logger.info(f"formed request: {formed_request}\nsecurity_risk: {security_risk}")
    if formed_request.is_valid() and security_risk < 75:
        return RequestFollowUp.ACCEPT
    if not isinstance(formed_request, UnIdentifiedUserRequest) and not formed_request.is_valid():
        return RequestFollowUp.REQUEST_FURTHER_DETAILS
    return RequestFollowUp.REJECT


def _formulate_reply_according_to_follow_up(
        formed_request: UserRequest, followup: RequestFollowUp
        ) -> list:
    """given a chosen course of action regarding a parsed requests, builds an appropriate response blocks."""
    reply_blocks = []
    if followup is RequestFollowUp.ACCEPT:
        reply_blocks.append(attitude.generate_approval_block())
    elif followup is RequestFollowUp.REQUEST_FURTHER_DETAILS:
        missing_fields = formed_request.get_missing_fields()
        reply_blocks.append(attitude.generate_request_for_fields(missing_fields))
    else:
        reply_blocks.append(attitude.generate_rejection_block())

    return reply_blocks


def _manage_cache_according_to_follow_up(
        formed_request: UserRequest, followup: RequestFollowUp, thread_ts: float
        ) -> None:
    """
    clears a request from the cache if its handling is complete (due to approval or rejection)
    or updates the cache in anticipation of more information from the user to be sent in a future message.
    """
    if followup in [RequestFollowUp.ACCEPT, RequestFollowUp.REJECT]:
        requests_map.pop(str(thread_ts), None)
    elif followup is RequestFollowUp.REQUEST_FURTHER_DETAILS:
        requests_map[str(thread_ts)] = formed_request
    else:
        logger.error(f"Encountered unknown followup request: {followup}")
