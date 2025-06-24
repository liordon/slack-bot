import unittest

from src.parsing.requests import UserRequest, RequestField


class _FakeRequest(UserRequest):
    def __init__(self, a: str, b: int):
        super(_FakeRequest, self).__init__(
            {
                "a": RequestField('a', 'a mandatory string field called a', True),
                "b": RequestField('b', 'an optional int field called b', False),
            }
        )
        self.a = a
        self.b = b


class BasicRequestActionsCase(unittest.TestCase):

    def test_given_a_request_mandatory_fields_can_be_distinguished_from_non_mandatory(self):
        req = _FakeRequest('a', 0)
        self.assertNotEquals(len(req._get_mandatory_fields()), len(req._field_details))

    def test_given_a_fully_assigned_request_there_are_no_missing_fields(self):
        req = _FakeRequest('a', 0)
        self.assertEqual(0, len(req.get_missing_fields()))

    def test_given_value_in_mandatory_field_then_request_is_valid(self):
        valid_req = _FakeRequest('a', None)
        self.assertTrue(valid_req.is_valid())

    def test_given_none_in_mandatory_field_then_request_is_invalid(self):
        invalid_req = _FakeRequest(None, 0)
        self.assertFalse(invalid_req.is_valid())

    def test_request_name_appears_in_pretty_print(self):
        req = _FakeRequest('a', 0)
        self.assertIn(req.__class__.__name__, req.pretty_print())

    def test_request_fields_and_descriptions_appears_in_pretty_print(self):
        req = _FakeRequest('a', 0)
        pretty_print = req.pretty_print()
        for field in req._field_details.values():
            self.assertIn(field.name, pretty_print)
            self.assertIn(field.description, pretty_print)


if __name__ == '__main__':
    unittest.main()
