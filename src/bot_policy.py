import logging
import uuid
from datetime import datetime, timezone

from cachetools import TTLCache
from slack_bolt import Say
from slack_sdk import WebClient

from src.auditing.bot_decision import BotDecision, BotDecisionResponse
from src.auditing.decision_logging import DecisionLogger
from src.conversational_user_interfaces.furry import Furry
from src.conversational_user_interfaces.professional import Professional
from src.parsing.constants import RequestFollowUp
from src.parsing.regex_classifier import attempt_to_classify, construct_according_to_classification
from src.parsing.requests import UnIdentifiedUserRequest, UserRequest
from src.security_estimator import calculate_security_risk

logging.basicConfig(level=logging.DEBUG)
flow_logger = logging.getLogger(__name__)
decision_logger = DecisionLogger()

requests_map = TTLCache(maxsize=100, ttl=1000*3600)
attitude = Furry()
security_risk_threshold = 75


def handle_message(message: dict, client: WebClient, say: Say, context) -> BotDecisionResponse:
    """
    Handles all incoming messages and checks if they are replies
    to the bot's own messages within a thread.

    Generic messages are ignored.
    Replies to existing threads are treated as a chance to fix partial security requests.
    """
    flow_logger.info(f"Received message: {message}")

    if __is_message_inside_a_thread(message):
        thread_root_ts = message['thread_ts']
        channel_id = message['channel']
        user_id = message['user']  # The user who replied

        flow_logger.info(f"Message is a thread reply. Thread TS: {thread_root_ts}")

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
                    return fix_previously_submitted_request(
                        message, say, thread_root_ts, user_id, client
                    )
                else:
                    flow_logger.info("Root message was not from this bot.")
            else:
                flow_logger.warning(
                    f"Could not retrieve root message for thread_ts: {thread_root_ts}"
                )

        except Exception as e:
            flow_logger.error(f"Error fetching thread history: {e}")

    return generate_irrelevant_response(message['text'])


def generate_irrelevant_response(user_message: str) -> BotDecisionResponse:
    return BotDecisionResponse(
        bot_decision=BotDecision(
            details=user_message,
            outcome=RequestFollowUp.IRRELEVANT,
        )
    )


def fix_previously_submitted_request(message, say, thread_root_ts, user_id, client) -> BotDecisionResponse:
    user_message = message['text']
    flow_logger.info(
        f"User '{user_id}' replied to our bot's message in thread: '{user_message}'"
    )
    thread_request = requests_map.get(str(thread_root_ts), None)
    old_ticket_id = str(uuid.uuid3(uuid.NAMESPACE_URL, str(thread_root_ts)))

    blocks = [
        attitude.generate_acknowledgement_block(message),
        attitude.generate_reflection_block(message),
    ]

    if thread_request is not None:
        completing_request = construct_according_to_classification(
            thread_request.request_type, user_message
        )

        merged_request = thread_request.merge_with(completing_request)
        security_risk = calculate_security_risk(merged_request)
        flow_logger.info(f"formed request: {merged_request}\nsecurity_risk: {security_risk}")

        followup = _decide_on_follow_up(merged_request, security_risk)
        _manage_cache_according_to_follow_up(merged_request, followup, thread_root_ts)

        blocks.append(
            attitude.generate_user_request_description_block(merged_request)
        )

        reply_blocks = _formulate_reply_according_to_follow_up(merged_request, followup)
        blocks.extend(reply_blocks)

        client.chat_postMessage(
            channel=message['channel'],
            thread_ts=thread_root_ts,
            blocks=blocks,
            text='hyper vyper has processed your request'
        )

        mandatory_field_names = [f.name for f in merged_request.get_mandatory_fields()]
        bot_decision = BotDecision(
            ticket_id=old_ticket_id,
            created_at=datetime.now(timezone.utc),
            request_type=merged_request.request_type,
            details=user_message,
            mandatory_fields=mandatory_field_names,
            fields_provided=[f for f in mandatory_field_names if
                getattr(merged_request, f) is not None],
            outcome=followup,
            security_risk=security_risk
        )
        decision_logger.log(bot_decision)
        bot_response = BotDecisionResponse(
            user_request=merged_request,
            response_in_chat=blocks,
            bot_decision=bot_decision,
        )
        return bot_response
    else:
        say(
            text=f"Hey <@{user_id}>! I'm sorry, but I closed the request in this thread due to timeout or completion. let's start over.",
            thread_ts=thread_root_ts
            # Ensure the reply goes back into the same thread
        )

        return generate_irrelevant_response(user_message)


def __we_initiated_this_thread(context, root_message):
    """compares our bot's ID to the ID of whoever initiated this thread to verify that it's indeed us."""
    return 'bot_id' in root_message and root_message['bot_id'] == context.bot_id


def __is_message_inside_a_thread(payload):
    """compares the thread_ts and ts fields of the message to determine whether it's inside an existing thread."""
    return 'thread_ts' in payload and payload['thread_ts'] != payload['ts']


def help_command(say):
    """returns the help output to the user"""
    b = attitude.generate_help_block()
    say(blocks=[b])


def classify_and_respond(payload, client) -> BotDecisionResponse:
    """This initiates a conversation about a security request."""
    blocks = [
        attitude.generate_acknowledgement_block(payload),
        attitude.generate_reflection_block(payload),
    ]
    new_ts = None

    flow_logger.debug(payload)
    channel = payload.get('channel_name')
    user_message = payload.get('text')
    request_type = attempt_to_classify(user_message)

    formed_request = construct_according_to_classification(request_type, user_message)
    flow_logger.debug(f"identified_request_type: {request_type}\nfrom user_message: {user_message}")

    blocks.append(attitude.generate_initial_classification_block(request_type))
    blocks.append(attitude.generate_user_request_description_block(formed_request))
    security_risk = calculate_security_risk(formed_request)

    followup = _decide_on_follow_up(formed_request, security_risk)
    reply_blocks = _formulate_reply_according_to_follow_up(formed_request, followup)
    blocks.extend(reply_blocks)

    mandatory_field_names = [f.name for f in formed_request.get_mandatory_fields()]
    bot_decision = BotDecision(
        ticket_id='invalid',
        created_at=datetime.now(timezone.utc),
        request_type=request_type,
        details=user_message,
        mandatory_fields=mandatory_field_names,
        fields_provided=[f for f in mandatory_field_names if getattr(formed_request, f) is not None],
        outcome=followup,
        security_risk=security_risk
    )
    bot_response = BotDecisionResponse(
        user_request=formed_request,
        response_in_chat=blocks,
        bot_decision=bot_decision,
    )
    try:
        response_data = client.chat_postMessage(
            channel=channel,
            blocks=blocks,
            text='hyper vyper has processed your request'
        )
        new_ts = response_data['ts']
        flow_logger.info(f"New request: {new_ts}")
        bot_response.thread_ts = new_ts

        _manage_cache_according_to_follow_up(formed_request, followup, new_ts)
        new_ticket_id = str(uuid.uuid3(uuid.NAMESPACE_URL, str(new_ts)))
        bot_decision.ticket_id = new_ticket_id
    except Exception as e:
        flow_logger.exception(e)
        flow_logger.error(blocks)
        flow_logger.error('Failed to respond to user')
    decision_logger.log(bot_decision)
    return bot_response


def _decide_on_follow_up(formed_request: UserRequest, security_risk: float) -> RequestFollowUp:
    """given a (possibly partial) request parsed from the user, decides what to do with it."""
    if formed_request.is_valid() and security_risk < security_risk_threshold:
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
        flow_logger.error(f"Encountered unknown followup request: {followup}")
