from enum import Enum


class RequestFollowUp(Enum):
    ACCEPT = 'accept'
    REJECT = 'reject'
    REQUEST_FURTHER_DETAILS = 'request_further_details'