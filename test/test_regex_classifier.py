import unittest
from src.regex_classifier import attempt_to_classify, attempt_to_construct_firewall_change, \
    attempt_to_construct_devtool_install, attempt_to_construct_cloud_access, attempt_to_construct_permissions_change, \
    attempt_to_construct_data_export
from src.constants import  RequestTypes
from src.requests import *


FULL_FIREWALL_CHANGE_REQUEST = '''Requesting temporary firewall rule to allow outbound SSH from bastion to vendor IP 196.181.12.201 on port 22.
This is for scheduled support session during the upcoming patch window.'''
FULL_DEVTOOL_INSTALL_REQUEST = '''Requesting installation of extension 'hold' from official VSCode marketplace.
Tool will be used by dev team for shared debugging and code review sessions.'''
FULL_PERMISSION_CHANGE_REQUEST = '''Requesting AdministratorAccess role for AWS account acme-prod to handle production incident.
Access needed for 3 hours. Related Jira ticket: INFRA-2171.'''
FULL_DATA_EXPORT_REQUEST = '''Request to export anonymized user event data (~43GB) for ML model training.
Data to be exported to secure S3 bucket acme-stage-medical. No direct identifiers present.'''
FULL_CLOUD_ACCESS_REQUEST = '''Access requested for S3 bucket acme-stage-radio to troubleshoot log ingestion failures.
Data classification: Internal. No customer PII involved.'''
FULL_NETWORK_ACCESS_REQUEST = '''Request to allow MySQL traffic from internal subnet 10.7.69.0/24 to RDS cluster rds-acme-dev.
This is needed for data sync during migration. Approved change window is 02:00–04:00 UTC.'''
FULL_VENDOR_APPROVAL_REQUEST = '''Flores, Garcia and Abbott provides marketing analytics services.
They completed ACME's security questionnaire with a passing score and have a valid SOC 2 Type II report. No PII involved.'''

class BasicClassificationTest(unittest.TestCase):
    def test_given_empty_request_then_result_is_unclassified(self):
        classification = attempt_to_classify('')
        self.assertEquals(RequestTypes.UNKNOWN, classification)

    def test_given_firewall_keyword_in_request_then_result_is_firewall_change(self):
        classification = attempt_to_classify(FULL_FIREWALL_CHANGE_REQUEST)
        self.assertEquals(RequestTypes.FIREWALL_CHANGE, classification)

    def test_given_install_keyword_in_request_then_result_is_devtool_install(self):
        classification = attempt_to_classify(FULL_DEVTOOL_INSTALL_REQUEST)
        self.assertEquals(RequestTypes.DEVTOOL_INSTALL, classification)

    def test_given_role_keyword_in_request_then_result_is_permission_change(self):
        classification = attempt_to_classify(FULL_PERMISSION_CHANGE_REQUEST)
        self.assertEquals(RequestTypes.PERMISSION_CHANGE, classification)

    def test_given_export_keyword_in_request_then_result_is_data_export(self):
        classification = attempt_to_classify(FULL_DATA_EXPORT_REQUEST)
        self.assertEquals(RequestTypes.DATA_EXPORT, classification)

    def test_given_access_keyword_in_request_then_result_is_cloud_access(self):
        classification = attempt_to_classify(FULL_CLOUD_ACCESS_REQUEST)
        self.assertEquals(RequestTypes.CLOUD_ACCESS, classification)

    def test_given_allow_traffic_keywords_in_request_then_result_is_network_access(self):
        classification = attempt_to_classify(FULL_NETWORK_ACCESS_REQUEST)
        self.assertEquals(RequestTypes.NETWORK_ACCESS, classification)

    def test_given_provide_keyword_in_request_then_result_is_vendor_approval(self):
        classification = attempt_to_classify(FULL_VENDOR_APPROVAL_REQUEST)
        self.assertEquals(RequestTypes.VENDOR_APPROVAL, classification)

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

class FireWallChangeConstructionTest(unittest.TestCase):
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
        self.assertEquals(duration, user_req.duraction)

    def test_given_manager_approval_in_request_then_appropriate_field_is_extracted(self):
        jira_ticket = 'PADAS-71070'
        user_req = attempt_to_construct_permissions_change(f"Jira ticket: {jira_ticket}")
        self.assertEquals(jira_ticket, user_req.manager_approval)

if __name__ == '__main__':
    unittest.main()
