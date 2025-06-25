import itertools
import unittest

from parameterized import parameterized

from src.parsing.requests import UserRequest, RequestField
from test.example_request_objects import (
    ALL_EMPTY_REQUESTS, FILLED_REQUESTS,
    ALTERNATE_FILLED_REQUESTS
)


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

    def merge_with(self, new_request: '_FakeRequest') -> '_FakeRequest':
        raise NotImplementedError()


class BasicRequestActionsCase(unittest.TestCase):

    def test_given_a_request_mandatory_fields_can_be_distinguished_from_non_mandatory(self):
        req = _FakeRequest('a', 0)
        self.assertNotEquals(len(req.get_mandatory_fields()), len(req._field_details))

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
        self.assertIn(req.__class__.__name__, req.pretty_print_description())

    def test_request_fields_and_descriptions_appears_in_pretty_print(self):
        req = _FakeRequest('a', 0)
        pretty_print = req.pretty_print_description()
        for field in req._field_details.values():
            self.assertIn(field.name, pretty_print)
            self.assertIn(field.description, pretty_print)


class RequestMergingCase(unittest.TestCase):

    @parameterized.expand(
        [
            (old, new) for old, new in itertools.product(ALL_EMPTY_REQUESTS, ALL_EMPTY_REQUESTS)
            if old.__class__ != new.__class__
        ]
    )
    def test_merging_with_different_request_class_produces_a_type_error(self, first_req, new_req):
        self.assertRaises(TypeError, lambda: first_req.merge_with(new_req))

    @parameterized.expand(
        [
            (old, new) for old, new in itertools.product(FILLED_REQUESTS, ALL_EMPTY_REQUESTS)
            if old.__class__ == new.__class__
        ]
    )
    def test_when_merging_empty_requests_into_filled_then_original_request_remains_unchanged(
            self, filled, empty
            ):
        self.assertEqual(filled, filled.merge_with(empty))

    @parameterized.expand(
        [
            (old, new) for old, new in itertools.product(FILLED_REQUESTS, ALTERNATE_FILLED_REQUESTS)
            if old.__class__ == new.__class__
        ]
    )
    def test_when_merging_between_filled_requests_then_original_request_is_altered(
            self, filled, also_filled
            ):
        self.assertNotEqual(filled, filled.merge_with(also_filled))


if __name__ == '__main__':
    unittest.main()
