"""
This module provides a furry conversation interface.
It should always be overly cutesy and sometimes downright bizarre.
"""
from typing import List

from src.conversational_user_interfaces.attitude import (
    Attitude, wrap_with_markdown_block, determine_indefinite_article
)
from src.parsing.requests import RequestField


class Furry(Attitude):
    """
    This is a furry conversation interface.
    It should always be overly cutesy and sometimes downright bizarre.
    """

    def generate_request_for_fields(self, missing_fields: List[RequestField]) -> dict:
        return wrap_with_markdown_block(
            "*OwO* ohnonono! senpai forgot some fields!\n" +
            f"{self._format_entire_missing_fields_list(missing_fields)}" +
            f"\n\nThis makes mesa sad!\n{_DOG}"
        )

    def generate_rejection_block(self) -> dict:
        return wrap_with_markdown_block(
            f"UwU I'm too good for you. consider yourself rejected.\n{_TOAD}"
        )

    def generate_approval_block(self) -> dict:
        return wrap_with_markdown_block(
            f"^w^ you are approved! here, have a bunny:\n{_BUNNY}"
        )

    def generate_acknowledgement_block(self, payload: dict) -> dict:
        return wrap_with_markdown_block(
            "UwU, time classify stuff for senpai! " +
            f"<@{payload.get('user_id')}>:"
        )

    def generate_initial_classification_block(self, classification: str) -> dict:
        return wrap_with_markdown_block(
            "lemme guessy! you want a " +
            determine_indefinite_article(classification) +
            classification + " request, right? mesa is amazeballs!"
        )

    def generate_help_block(self) -> dict:
        return wrap_with_markdown_block(
            "UwU My name is hypa vypa! Imma help senpai " +
            "to get your security stiffy going in a jiffy!\n" +
            "Use the `/classify` command and say what you need to do, " +
            f"and I will make it happen! I'll be good, promise!\n{_CAT}"

        )

    def generate_closed_request_block(self) -> dict:
        return wrap_with_markdown_block(
            "OwO it looks like I closed this request! tough luck!\nSenpai wanna try again?"
        )


_BUNNY = """
  //
 ('>
 /rr
*\))_"""

_DOG = """
  __      _
o^^)}____//
 `_/      )
 (__(__/-(_/"""

_TOAD = """
       (.)(.)
   ,-.(.____.),-.
  ( \ \ '--' / / )
   \ \ / ,. \ / /
    ) '| || |' (
OoO'- OoO''OoO -'OoO"""

_CAT = """
    |\__/,|   (`\\
  _.|o o  |_   ) )
-(((---(((--------"""
