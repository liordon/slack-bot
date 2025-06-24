import unittest
from src.bot_policy import classify_command
from src.parsing.requests import *

basic_fake_payload = {
    'token': '6gXYiea8a5GXPFnyHHjdqnYi',
    'team_id': 'T092VDAJ9CY',
    'team_domain': 'liordonezia',
    'channel_id': 'C092HGG2GSW',
    'channel_name': 'secret-tests',
    'user_id': 'U092VDAKQG0',
    'user_name': 'liordon',
    'command': '/classify',
    'text': 'shambalulu',
    'api_app_id': 'A092VE1A908',
    'is_enterprise_install': 'false',
    'response_url': 'https://hooks.slack.com/commands/T092VDAJ9CY/9085297732050/PWuAI3SZPBwEaYbS7z5ovEis',
    'trigger_id': '9085297761442.9097452621440.cf87cc75ae3c97cddfc3d8b4e662e54a'
}

NULL_ACK = lambda :None

def create_payload_with_text(txt: str) -> dict:
    output = basic_fake_payload.copy()
    output['text'] = txt
    return output

class MyTestCase(unittest.TestCase):
    def test_given_unparsable_request_then_result_is_unclassified(self):
        response = classify_command(basic_fake_payload, NULL_ACK)
        self.assertIsInstance(response, UnIdentifiedUserRequest)

    def test_given_every_required_field_for_Firewall_Change_request_then_result_is_firewall_change(self):
        fake_fw_change_payload = create_payload_with_text('Allow SSH to external IP 196.181.12.201 on port 22')
        response = classify_command(fake_fw_change_payload, NULL_ACK)
        self.assertIsInstance(response, FireWallChangeRequest)

if __name__ == '__main__':
    unittest.main()
