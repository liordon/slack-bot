"""
An interface governing the conversational user interface of the chatbot.
Different implementations of this class serve as "skins" of the application,
allowing the user to pick the attitude that speaks best to them.
"""
from abc import ABC, abstractmethod
from typing import List

from src.parsing.requests import UserRequest, RequestField


def _format_missing_field(missing_field: RequestField) -> str:
    """
    Converts a field to a pretty-printed string that can be forwarded to the user with any attitude.
    """
    return f"*<{missing_field.name.replace('_', ' ')}>*: " + \
        ('mandatory' if missing_field.is_required else '_optional_') + \
        f"\n{missing_field.description}\n"


class Attitude(ABC):
    """
    An interface governing the conversational user interface of the chatbot.
    Different implementations of this class serve as "skins" of the application,
    allowing the user to pick the attitude that speaks best to them.
    """

    @abstractmethod
    def generate_acknowledgement_block(self, payload: dict) -> dict:
        """Generates a block that acknowledges the user's last message."""
        pass

    @abstractmethod
    def generate_rejection_block(self) -> dict:
        """Generates a block that rejects the user's security request."""
        pass

    @abstractmethod
    def generate_approval_block(self) -> dict:
        """Generates a block that approves the user's security request."""
        pass

    @abstractmethod
    def generate_request_for_fields(self, missing_fields: List[RequestField]) -> dict:
        """Generates a block that requests the user for fields missing in his security request."""
        pass

    @staticmethod
    def _format_entire_missing_fields_list(missing_fields: List[RequestField]) -> str:
        """pretty prints all the missing fields from the user's request."""
        formatted_fields = [_format_missing_field(f) for f in missing_fields]
        return '\n'.join(formatted_fields)

    @staticmethod
    def generate_reflection_block(payload: dict) -> dict:
        """Generates a block that reflects the user's last message as a quote."""
        request_lines = payload.get('text').split('\n')
        return wrap_with_markdown_block('>' + '\n>'.join(request_lines))

    @abstractmethod
    def generate_initial_classification_block(self, classification: str) -> dict:
        """Generates a block that informs the user of how we classified his request."""
        pass

    @staticmethod
    def generate_user_request_description_block(user_request: UserRequest) -> dict:
        """Generates a block that informs the user of how we parsed his request in detail."""
        return wrap_with_markdown_block(user_request.pretty_print())


def wrap_with_markdown_block(txt: str) -> dict:
    """Wraps a text in a json markdown block"""
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": txt
        }
    }


def determine_indefinite_article(word: str) -> str:
    """determines the indefinite article of a word (a or an)"""
    if word.lower()[0] in 'aeiouy':
        return 'an'
    else:
        return 'a'
