import unittest
from unittest.mock import MagicMock

from src.bot_policy import classify_and_respond, handle_message
from src.parsing.requests import UnIdentifiedUserRequest, FireWallChangeRequest

basic_fake_payload = {
    'token': '6gXYiea8a5GXPFnyHHjdqnYi',
    'team_id': 'T092VDAJ9CY',
    'team_domain': 'liordonezia',
    'channel': 'secret-tests-channel',
    'channel_id': 'C092HGG2GSW',
    'channel_name': 'secret-tests',
    'user': 'shambalulu',
    'user_id': 'U092VDAKQG0',
    'user_name': 'liordon',
    'command': '/classify',
    'text': 'shambalulu',
    'api_app_id': 'A092VE1A908',
    'is_enterprise_install': 'false',
    'response_url': 'https://hooks.slack.com/commands/T092VDAJ9CY/9085297732050/PWuAI3SZPBwEaYbS7z5ovEis',
    'trigger_id': '9085297761442.9097452621440.cf87cc75ae3c97cddfc3d8b4e662e54a'
}

VYPER_ID = 'hyper-vyper'


def create_fresh_payload_with_text(txt: str) -> dict:
    output = basic_fake_payload.copy()
    output['text'] = txt
    return output


def create_threaded_payload_with_text(txt: str, thread_ts) -> dict:
    output = basic_fake_payload.copy()
    output['text'] = txt
    output['thread_ts'] = thread_ts
    output['ts'] = thread_ts + 1
    return output


class ConversationalFlowCase(unittest.TestCase):
    def test_given_unparsable_request_then_result_is_unclassified(self):
        user_request, chatbot_response, new_thread_ts = classify_and_respond(
            basic_fake_payload, MagicMock()
        )
        self.assertIsInstance(user_request, UnIdentifiedUserRequest)

    def test_given_every_required_field_for_Firewall_Change_request_then_result_is_firewall_change(
            self
    ):
        fake_fw_change_payload = create_fresh_payload_with_text(
            'Allow SSH to external IP 196.181.12.201 on port 22'
        )
        user_request, chatbot_response, new_thread_ts = classify_and_respond(
            fake_fw_change_payload, MagicMock()
        )
        self.assertIsInstance(user_request, FireWallChangeRequest)

    def test_given_every_required_field_for_a_request_then_result_has_valid_blocks(self):
        fake_fw_change_payload = create_fresh_payload_with_text(
            'Allow SSH to external IP 196.181.12.201 on port 22'
        )
        user_request, chatbot_response_blocks, new_thread_ts = classify_and_respond(
            fake_fw_change_payload, MagicMock()
        )
        for index, block in enumerate(chatbot_response_blocks):
            self.assertIsNotNone(block, f"block {index} is None")

    def test_given_partial_request_then_result_is_saved_for_future_correspondence(self):
        portless_fw_change_req = create_fresh_payload_with_text(
            'allow ssh to external ip from 127.0.0.1 to 666.666.666.666'
        )
        threading_client = MagicMock()
        threading_client.chat_postMessage.return_value = {'ts': 42.0}
        threading_client.conversations_history.return_value = {
            'ok': True,
            'messages': [{'bot_id': VYPER_ID}]
        }
        user_request, chatbot_response_blocks, new_thread_ts = classify_and_respond(
            portless_fw_change_req, threading_client
        )
        new_reminder = create_threaded_payload_with_text('are you still there?', new_thread_ts)
        bot_context = MagicMock()
        bot_context.bot_id = VYPER_ID
        recalled_request, new_response_blocks = handle_message(
            new_reminder, threading_client, MagicMock(), bot_context
        )
        self.assertEqual(user_request, recalled_request)


if __name__ == '__main__':
    unittest.main()
