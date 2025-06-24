from typing import List

from src.conversational_user_interfaces.attitude import Attitude, wrap_with_markdown_block, determine_indefinite_article
from src.parsing.fields import MissingField


class Professional(Attitude):
    def generate_refusal_block_for_thread(self):
        return wrap_with_markdown_block(f"Unfortunately, I am unable to process new requests within existing threads.")

    def generate_request_for_fields(self, missing_fields: List[MissingField]) -> dict:
        return wrap_with_markdown_block(f"I must ask you to fill in the following fields:\n{self._format_entire_missing_fields_list(missing_fields)}")

    def generate_rejection_block(self, payload: dict) -> dict:
        return wrap_with_markdown_block(f"I regret to inform you that your request has been rejected.")

    def generate_approval_block(self, payload: dict) -> dict:
        return wrap_with_markdown_block(f"I am delighted to inform you that your request has been approved.")

    def generate_acknowledgement_block(self, payload: dict) -> dict:
        return wrap_with_markdown_block(f"I Received a *slash command* to classify the following input for <@{payload.get('user_id')}>:")

    def generate_initial_classification_block(self, classification: str) -> dict:
        return wrap_with_markdown_block(f"from what I gather, this is {determine_indefinite_article(classification)} {classification} request.")