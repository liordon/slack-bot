"""
This module provides a professional conversation interface.
It should always be polite, informative and patient
"""
from typing import List

from src.conversational_user_interfaces.attitude import (
    Attitude, wrap_with_markdown_block, determine_indefinite_article
)
from src.parsing.requests import RequestField


class Professional(Attitude):
    """
    This is a professional conversation interface.
    It should always be polite, informative and patient
    """

    def generate_request_for_fields(self, missing_fields: List[RequestField]) -> dict:
        return wrap_with_markdown_block(
            "*ERROR* I must ask you to fill in the following fields:\n" +
            f"{self._format_entire_missing_fields_list(missing_fields)}"
        )

    def generate_rejection_block(self) -> dict:
        return wrap_with_markdown_block(
            "I regret to inform you that your request has been rejected."
        )

    def generate_approval_block(self) -> dict:
        return wrap_with_markdown_block(
            "I am delighted to inform you that your request has been approved."
        )

    def generate_acknowledgement_block(self, payload: dict) -> dict:
        return wrap_with_markdown_block(
            "I Received a *slash command* to classify the following input for " +
            f"<@{payload.get('user_id')}>:"
        )

    def generate_initial_classification_block(self, classification: str) -> dict:
        return wrap_with_markdown_block(
            "from what I gather, this is " +
            determine_indefinite_article(classification) +
            classification + " request."
        )

    def generate_help_block(self) -> dict:
        return wrap_with_markdown_block("I'm sorry, but you cannot be helped.")

    def generate_closed_request_block(self) -> dict:
        return wrap_with_markdown_block(
            "I'm sorry, but I closed the request in this thread due to timeout or completion. " +
            "let's start over."
        )