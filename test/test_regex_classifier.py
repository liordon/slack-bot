import unittest

from parameterized import parameterized

from src.parsing.regex_classifier import attempt_to_classify, attempt_to_construct_firewall_change, \
    attempt_to_construct_devtool_install, attempt_to_construct_cloud_access, attempt_to_construct_permissions_change, \
    attempt_to_construct_data_export, attempt_to_construct_vendor_approval, attempt_to_construct_network_access, \
    construct_according_to_classification
from src.parsing.constants import RequestTypes
from src.parsing.requests import *
from test.example_request_texts import FULL_FIREWALL_CHANGE_REQUEST, FULL_DEVTOOL_INSTALL_REQUEST, \
    FULL_PERMISSION_CHANGE_REQUEST, FULL_DATA_EXPORT_REQUEST, FULL_CLOUD_ACCESS_REQUEST, FULL_NETWORK_ACCESS_REQUEST, \
    FULL_VENDOR_APPROVAL_REQUEST


def _generate_name_for_type_test(testcase_func, param_num, param):
    retval = parameterized.to_safe_name(f"{testcase_func.__name__}_{param_num}_{param.args[1]}")
    return parameterized.to_safe_name(f"{testcase_func.__name__}_{param_num}_{param.args[1]}")

class BasicClassificationTest(unittest.TestCase):
    def test_given_empty_request_then_result_is_unclassified(self):
        classification = attempt_to_classify('')
        self.assertEquals(RequestTypes.UNKNOWN, classification)

    @parameterized.expand([
            (FULL_CLOUD_ACCESS_REQUEST, RequestTypes.CLOUD_ACCESS),
            (FULL_DATA_EXPORT_REQUEST, RequestTypes.DATA_EXPORT),
            (FULL_DEVTOOL_INSTALL_REQUEST, RequestTypes.DEVTOOL_INSTALL),
            (FULL_FIREWALL_CHANGE_REQUEST, RequestTypes.FIREWALL_CHANGE),
            (FULL_NETWORK_ACCESS_REQUEST, RequestTypes.NETWORK_ACCESS),
            (FULL_PERMISSION_CHANGE_REQUEST, RequestTypes.PERMISSION_CHANGE),
            (FULL_VENDOR_APPROVAL_REQUEST, RequestTypes.VENDOR_APPROVAL),
        ], name_func=_generate_name_for_type_test)
    def test_given_full_message_then_the_appropriate_request_is_constructed(self, classification, type_name):
        self.assertEquals(type_name, attempt_to_classify(classification))

    @parameterized.expand([
            (CloudResourceAccessRequest, RequestTypes.CLOUD_ACCESS),
            (DataExportRequest, RequestTypes.DATA_EXPORT),
            (DevToolInstallRequest, RequestTypes.DEVTOOL_INSTALL),
            (FireWallChangeRequest, RequestTypes.FIREWALL_CHANGE),
            (NetworkAccessRequest, RequestTypes.NETWORK_ACCESS),
            (PermissionsChangeRequest, RequestTypes.PERMISSION_CHANGE),
            (VendorApprovalRequest, RequestTypes.VENDOR_APPROVAL),
        ], name_func=_generate_name_for_type_test)
    def test_given_classification_then_the_appropriate_request_is_constructed(self, request_type, type_name):
        self.assertIsInstance(construct_according_to_classification(type_name, ''), request_type)


class CloudAccessTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_req = attempt_to_construct_cloud_access(FULL_CLOUD_ACCESS_REQUEST)
        self.assertIsInstance(user_req, CloudResourceAccessRequest)

    def test_given_justification_in_request_then_appropriate_field_is_extracted(self):
        justification = 'defeating terrorism once and for all'
        user_req = attempt_to_construct_cloud_access(f"to {justification}")
        self.assertEquals(justification, user_req.business_justification)

    def test_given_data_sensitivity_in_request_then_appropriate_field_is_extracted(self):
        sensitivity = 'secretive. customer PII at risk'
        user_req = attempt_to_construct_cloud_access(f"Data classification: {sensitivity}")
        self.assertEquals(sensitivity, user_req.sensitivity)


class DataExportTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_req = attempt_to_construct_data_export(FULL_DATA_EXPORT_REQUEST)
        self.assertIsInstance(user_req, DataExportRequest)

    def test_given_business_justification_in_request_then_justification_is_extracted(self):
        justification = 'quarterly compliance audit'
        user_req = attempt_to_construct_data_export(f"export data for {justification}.")
        self.assertEqual(justification, user_req.business_justification)

    @unittest.skip("non-mandatory field")
    def test_given_pii_involved_explicitly_then_pii_is_true(self):
        user_req = attempt_to_construct_data_export("Sensitive PII involved in this data export.")
        self.assertTrue(user_req.pii_involved)

    @unittest.skip("non-mandatory field")
    def test_given_no_pii_involved_explicitly_then_pii_is_false(self):
        user_req = attempt_to_construct_data_export("Export data. No PII is included.")
        self.assertFalse(user_req.pii_involved)

    def test_given_data_destination_in_request_then_destination_is_extracted(self):
        destination = 'secure-gcp-bucket-prod'
        user_req = attempt_to_construct_data_export(f"Data to be exported to {destination}.")
        self.assertEqual(destination, user_req.destination)

    @unittest.skip("non-mandatory field")
    def test_given_data_volume_in_request_then_volume_is_extracted(self):
        user_req_1 = attempt_to_construct_data_export("Export 10GB of data.")
        self.assertEqual(user_req_1.data_volume_gb, 10.0)

        user_req_2 = attempt_to_construct_data_export(
            "Data volume approx 500MB.")  # If you handle MB, adjust expected value
        # self.assertEqual(user_req_2.data_volume_gb, 0.5)

        user_req_3 = attempt_to_construct_data_export(
            "Data size: ~2.5TB for research.")  # If you handle TB, adjust expected value
        # self.assertEqual(user_req_3.data_volume_gb, 2500.0)

    def test_given_missing_mandatory_field_then_field_is_none(self):
        # Test case where business justification is missing
        user_req = attempt_to_construct_data_export("Export data to secure S3 bucket acme-dev. No PII.")
        self.assertIsNone(user_req.business_justification)


class DevtoolInstallTest(unittest.TestCase):
    def test_given_example_input_then_devtool_install_request_is_created(self):
        user_req = attempt_to_construct_devtool_install(FULL_DEVTOOL_INSTALL_REQUEST)
        self.assertIsInstance(user_req, DevToolInstallRequest)

    def test_given_justification_in_request_then_appropriate_field_is_extracted(self):
        justification = 'creating secret logic bombs in code'
        user_req = attempt_to_construct_devtool_install(f"tool will be used for {justification}")
        self.assertEquals(justification, user_req.business_justification)

    def test_given_team_leader_approval_in_request_then_appropriate_field_is_extracted(self):
        ticket = 'JUCHA-7979'
        user_req = attempt_to_construct_devtool_install(f"Jira ticket: {ticket}")
        self.assertEquals(ticket, user_req.team_leader_approval)


class FireWallChangeTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_req = attempt_to_construct_firewall_change(FULL_FIREWALL_CHANGE_REQUEST)
        self.assertIsInstance(user_req, FireWallChangeRequest)
        self.assertTrue(user_req.is_valid())

    def test_given_source_system_in_request_then_appropriate_field_is_extracted(self):
        source_system = 'very deep shambalulu'
        user_req = attempt_to_construct_firewall_change(f"from {source_system}")
        self.assertEqual(source_system, user_req.source_system)

    def test_given_destination_address_in_request_then_appropriate_field_is_extracted(self):
        dest_ip = '127.0.0.1'
        dest_port = 666
        user_req = attempt_to_construct_firewall_change(f"to vendor IP {dest_ip} on port {dest_port}")
        self.assertEqual(f"{dest_ip}:{dest_port}", user_req.destination_ip)

    def test_given_any_justification_in_request_then_appropriate_field_is_extracted(self):
        justification = 'creating a backdoor for Laplandian hackers'
        user_req = attempt_to_construct_firewall_change(f"for {justification}")
        self.assertEqual(justification, user_req.business_justification)


class NetworkAccessTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_request = attempt_to_construct_network_access(FULL_NETWORK_ACCESS_REQUEST)
        self.assertIsInstance(user_request, NetworkAccessRequest)

    def test_given_business_justification_in_request_then_appropriate_field_is_extracted(self):
        justification = 'writing more refined scifi stories'
        user_req = attempt_to_construct_network_access(f"this is needed for {justification}")
        self.assertEquals(justification, user_req.business_justification)

    def test_given_source_cidr_in_request_then_appropriate_field_is_extracted(self):
        cidr = '10.7.69.0/24'
        user_req = attempt_to_construct_network_access(
            f"allow MySQL traffic from internal subnet {cidr} to RDS cluster rds-acme-dev")
        self.assertEquals(cidr, user_req.source_cidr)


class PermissionChangeTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_request = attempt_to_construct_permissions_change(FULL_PERMISSION_CHANGE_REQUEST)
        self.assertIsInstance(user_request, PermissionsChangeRequest)

    def test_given_justification_in_request_then_appropriate_field_is_extracted(self):
        justification = 'develop a new kind of flubber'
        user_req = attempt_to_construct_permissions_change(f"to {justification}")
        self.assertEquals(justification, user_req.business_justification)

    def test_given_duration_in_request_then_appropriate_field_is_extracted(self):
        duration = '42 hours'
        user_req = attempt_to_construct_permissions_change(f"make me an admin for {duration}")
        self.assertEquals(duration, user_req.duration)

    def test_given_manager_approval_in_request_then_appropriate_field_is_extracted(self):
        jira_ticket = 'PADAS-71070'
        user_req = attempt_to_construct_permissions_change(f"Jira ticket: {jira_ticket}")
        self.assertEquals(jira_ticket, user_req.manager_approval)

    # ... inside PermissionChangeTest(unittest.TestCase):
    def test_given_aws_account_in_request_then_account_is_extracted(self):
        aws_account = 'acme-test-env'
        user_req = attempt_to_construct_permissions_change(f"Requesting role for AWS account {aws_account}.")
        self.assertEqual(aws_account, user_req.aws_account)

    def test_given_role_requested_in_request_then_role_is_extracted(self):
        role_requested = 'ReadOnlyAccess'
        user_req = attempt_to_construct_permissions_change(f"Requesting {role_requested} role.")
        self.assertEqual(role_requested, user_req.role_requested)


class VendorApprovalTest(unittest.TestCase):
    def test_given_full_request_then_valid_request_can_be_extracted(self):
        user_request = attempt_to_construct_vendor_approval(FULL_VENDOR_APPROVAL_REQUEST)
        self.assertIsInstance(user_request, VendorApprovalRequest)
        self.assertIsNotNone(user_request.vendor_name)
        self.assertIsNotNone(user_request.security_questionnaire_completed)
        self.assertIsNotNone(user_request.data_classification)
        self.assertIsNotNone(user_request.legal_review_completed)

    def test_given_vendor_name_in_request_then_name_is_extracted(self):
        vendor = 'Acne Solutions'
        user_req = attempt_to_construct_vendor_approval(f"{vendor} provide solutions for pimple epidemics.")
        self.assertEqual(vendor, user_req.vendor_name)

    def test_given_no_pii_involved_then_pii_is_false(self):
        pii_involvement = "No PII involved"
        user_req = attempt_to_construct_vendor_approval(pii_involvement)
        self.assertEquals(pii_involvement, user_req.data_classification)

    def test_given_attestation_of_security_questionnaire_in_request_then_appropriate_field_is_set(self):
        pii_involvement = "I completed ACME's security questionnaire with a failing score"
        user_req = attempt_to_construct_vendor_approval(pii_involvement)
        self.assertFalse(user_req.security_questionnaire_completed)
        self.assertIsNotNone(user_req.security_questionnaire_completed)

    def test_given_evidence_of_security_report_validity_in_request_then_appropriate_field_is_set(self):
        pii_involvement = "I don't have a valid SOC 2 Type II report."
        user_req = attempt_to_construct_vendor_approval(pii_involvement)
        self.assertFalse(user_req.security_questionnaire_completed)
        self.assertIsNotNone(user_req.legal_review_completed)


if __name__ == '__main__':
    unittest.main()
