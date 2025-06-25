from datetime import datetime
from dataclasses import dataclass

from typing import List

from src.parsing.constants import RequestFollowUp
from src.parsing.requests import UserRequest


@dataclass
class BotDecision(object):
    ticket_id: str = 'invalid'
    created_at: datetime = None
    request_type: str = None
    request_summary: str = None
    details: str = None
    mandatory_fields: list = None
    fields_provided: list = None
    outcome: RequestFollowUp = None
    security_risk: int = None

@dataclass
class BotDecisionResponse(object):
    user_request: UserRequest = None
    response_in_chat: List[dict] = None
    thread_ts: float = None
    bot_decision: BotDecision = None