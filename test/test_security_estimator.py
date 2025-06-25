import itertools
import unittest

from parameterized import parameterized

from src.security_estimator import calculate_security_risk
from test.example_request_objects import (
    ALL_EMPTY_REQUESTS,
    FILLED_REQUESTS,
    ALTERNATE_FILLED_REQUESTS
)


class MyTestCase(unittest.TestCase):
    @parameterized.expand(ALL_EMPTY_REQUESTS)
    def test_when_calculating_an_empty_request_then_result_is_100(self, request):
        self.assertEqual(100, calculate_security_risk(request))  # add assertion here

    @parameterized.expand(FILLED_REQUESTS)
    def test_when_calculating_a_filled_request_then_result_is_repeatable(self, request):
        self.assertEqual(
            calculate_security_risk(request), calculate_security_risk(request)
            )  # add assertion here

    @parameterized.expand(
        [
            (old, new) for old, new in itertools.product(FILLED_REQUESTS, ALTERNATE_FILLED_REQUESTS)
            if old.__class__ == new.__class__
        ]
    )
    def test_when_calculating_filled_requests_then_result_is_dependent_on_fields(
            self, req1, req2
    ):
        self.assertNotEqual(
            calculate_security_risk(req1),
            calculate_security_risk(req2),
            "expected different score " +
            f"\nfor {req1.pretty_print_content()} \n\nand {req2.pretty_print_content()}"
        )


if __name__ == '__main__':
    unittest.main()
