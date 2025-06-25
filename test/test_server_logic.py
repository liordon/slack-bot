import unittest
from unittest.mock import MagicMock

from src import bot_policy
from src.bot_policy import classify_and_respond, handle_message
from src.parsing.constants import RequestFollowUp
from src.parsing.requests import UnIdentifiedUserRequest, FireWallChangeRequest
from test.example_request_texts import FULL_FIREWALL_CHANGE_REQUEST

VYPER_ID = 'hyper-vyper'


class ConversationalFlowCase(unittest.TestCase):

    def setUp(self):
        bot_policy.decision_logger.log = MagicMock()

        self.threading_client = MagicMock()
        self.threading_client.chat_postMessage.return_value = {'ts': 42.0}
        self.threading_client.conversations_history.return_value = {
            'ok': True,
            'messages': [{'bot_id': VYPER_ID}]
        }

        self.bot_context = MagicMock()
        self.bot_context.bot_id = VYPER_ID

    def test_given_unparsable_request_then_result_is_unclassified(self):
        bot_response = classify_and_respond(
            _basic_fake_payload, MagicMock()
        )
        self.assertIsInstance(bot_response.user_request, UnIdentifiedUserRequest)

    def test_given_unparsable_request_then_followup_is_reject(self):
        bot_response = classify_and_respond(
            _basic_fake_payload, MagicMock()
        )
        self.assertEqual(RequestFollowUp.REJECT, bot_response.bot_decision.outcome)

    def test_given_every_required_field_for_Firewall_Change_request_then_result_is_firewall_change(
            self
    ):
        fake_fw_change_payload = create_fresh_payload_with_text(
            'Allow SSH to external IP 196.181.12.201 on port 22'
        )
        bot_response = classify_and_respond(
            fake_fw_change_payload, MagicMock()
        )
        self.assertIsInstance(bot_response.user_request, FireWallChangeRequest)

    def test_given_every_required_field_for_Firewall_Change_request_then_followup_is_accept(
            self
    ):
        fake_fw_change_payload = create_fresh_payload_with_text(
            FULL_FIREWALL_CHANGE_REQUEST
        )
        bot_response = classify_and_respond(
            fake_fw_change_payload, MagicMock()
        )
        self.assertEqual(RequestFollowUp.ACCEPT, bot_response.bot_decision.outcome)

    def test_given_every_required_field_for_a_request_then_result_has_valid_blocks(self):
        fake_fw_change_payload = create_fresh_payload_with_text(
            'Allow SSH to external IP 196.181.12.201 on port 22'
        )
        bot_response = classify_and_respond(
            fake_fw_change_payload, MagicMock()
        )
        for index, block in enumerate(bot_response.response_in_chat):
            self.assertIsNotNone(block, f"block {index} is None")

        bot_response = classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )

        self.assertEqual(RequestFollowUp.REQUEST_FURTHER_DETAILS, bot_response.bot_decision.outcome)

    def test_given_partial_request_then_result_is_saved_for_future_correspondence(self):
        bot_response = classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )
        new_reminder = create_threaded_payload_with_text(
            'are you still there?', bot_response.thread_ts
        )
        updated_bot_decision = handle_message(
            new_reminder, self.threading_client, MagicMock(), self.bot_context
        )
        self.assertEqual(bot_response.user_request, updated_bot_decision.user_request)

    def test_given_partial_request_then_bot_decision_records_missing_mandatory_fields(self):
        bot_response = classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )

        self.assertNotEqual(
            bot_response.bot_decision.mandatory_fields,
            bot_response.bot_decision.fields_provided
        )
        self.assertNotEqual(
            0,
            len(bot_response.bot_decision.fields_provided)
        )

    def test_given_partial_request_followed_by_missing_field_then_original_user_request_is_fixed(
            self
    ):
        bot_response = classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )
        new_reminder = create_threaded_payload_with_text(
            'send it to 666.666.666.666 on port 22', bot_response.thread_ts
        )
        updated_bot_decision = handle_message(
            new_reminder, self.threading_client, MagicMock(), self.bot_context
        )
        self.assertNotEqual(bot_response.user_request, updated_bot_decision.user_request)
        self.assertTrue(updated_bot_decision.user_request.is_valid())
        self.assertEqual(RequestFollowUp.ACCEPT, updated_bot_decision.bot_decision.outcome)

    def test_initial_bot_interaction_is_written_to_log(self):
        classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )

        bot_policy.decision_logger.log.assert_called_once()

    def test_successful_request_completion_is_written_to_log_anew(self):
        bot_response = classify_and_respond(
            _portless_fw_change_req, self.threading_client
        )

        bot_policy.decision_logger.log = MagicMock()

        new_message = create_threaded_payload_with_text(
            'send it to 666.666.666.666 on port 42', bot_response.thread_ts
        )

        handle_message(
            new_message, self.threading_client, MagicMock(), self.bot_context
        )

        bot_policy.decision_logger.log.assert_called_once()


_basic_fake_payload = {
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


def create_fresh_payload_with_text(txt: str) -> dict:
    output = _basic_fake_payload.copy()
    output['text'] = txt
    return output


_portless_fw_change_req = create_fresh_payload_with_text(
    'allow ssh to external ip from 127.0.0.1 to 666.666.666.666'
)


def create_threaded_payload_with_text(txt: str, thread_ts) -> dict:
    output = _basic_fake_payload.copy()
    output['text'] = txt
    output['thread_ts'] = thread_ts
    output['ts'] = thread_ts + 1
    return output


if __name__ == '__main__':
    unittest.main()
