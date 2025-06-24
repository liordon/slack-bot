from abc import ABC, abstractmethod
from typing import List

from src.parsing.fields import MissingField

class Attitude(ABC):
    @abstractmethod
    def generate_acknowledgement_block(self, payload: dict) -> dict:
        pass

    @abstractmethod
    def generate_rejection_block(self, payload: dict) -> dict:
        pass

    @abstractmethod
    def generate_approval_block(self, payload: dict) -> dict:
        pass

    @abstractmethod
    def generate_request_for_fields(self, missing_fields: List[MissingField]) -> dict:
        pass

    def _format_entire_missing_fields_list(self, missing_fields: List[MissingField]) -> str:
        formatted_fields = [self._format_missing_field(f) for f in missing_fields]
        return '\n'.join(formatted_fields)

    def generate_reflection_block(self, payload: dict) -> dict:
        request_lines = payload.get('text').split('\n')
        return wrap_with_markdown_block('>'+'\n>'.join(request_lines))

    @abstractmethod
    def generate_initial_classification_block(self, classification: str) -> dict:
        pass

    def _format_missing_field(self, missing_field: MissingField) -> str:
        return f"*<{missing_field.name.replace('_',' ')}>*: " + ('mandatory' if missing_field.is_required else '_optional_') + f"\n{missing_field.description}\n"

    @abstractmethod
    def generate_refusal_block_for_thread(self):
        pass

def wrap_with_markdown_block(txt: str) -> dict:
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": txt
        }
    }

def determine_indefinite_article(word: str) -> str:
    if word.lower()[0] in 'aeiouy':
        return 'an'
    else:
        return 'a'