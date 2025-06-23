import re

from typing import Callable, Any

from src.requests import *
from src.constants import *

def attempt_to_classify(text: str) -> str:
    if __firewall_preamble.search(text):
        return RequestTypes.FIREWALL_CHANGE
    if 'install' in text:
        return RequestTypes.DEVTOOL_INSTALL
    if 'role' in text:
        return RequestTypes.PERMISSION_CHANGE
    if 'export' in text:
        return RequestTypes.DATA_EXPORT
    if 'access' in text.lower():
        return RequestTypes.CLOUD_ACCESS
    if __allow_traffic.search(text):
        return RequestTypes.NETWORK_ACCESS
    if __provide_services.search(text):
        return RequestTypes.VENDOR_APPROVAL
    return RequestTypes.UNKNOWN

def construct_according_to_classification(classification: str, txt:str) -> UserRequest:
    if classification == RequestTypes.CLOUD_ACCESS:
        return attempt_to_construct_cloud_access(txt)
    elif classification == RequestTypes.DATA_EXPORT:
        return attempt_to_construct_data_export(txt)
    elif classification == RequestTypes.DEVTOOL_INSTALL:
        return attempt_to_construct_devtool_install(txt)
    elif classification == RequestTypes.FIREWALL_CHANGE:
        return attempt_to_construct_firewall_change(txt)
    elif classification == RequestTypes.NETWORK_ACCESS:
        return attempt_to_construct_network_access(txt)
    elif classification == RequestTypes.PERMISSION_CHANGE:
        return attempt_to_construct_permissions_change(txt)
    elif classification == RequestTypes.VENDOR_APPROVAL:
        return attempt_to_construct_vendor_approval(txt)
    else:
        return UnIdentifiedUserRequest()

def extract_if_found(regex: re.Pattern, text: str, extractor: Callable[[re.Match], Any]) -> Any:
    match = regex.search(text)
    if match is not None:
        return extractor(match)
    else:
        return None


def attempt_to_construct_cloud_access(text: str) -> CloudResourceAccessRequest:
    access_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    sensitivity = extract_if_found(__data_sensitivity_pattern, text, lambda m: m.group('sensitivity'))
    return CloudResourceAccessRequest(access_reason, sensitivity)


def attempt_to_construct_data_export(text: str) -> DataExportRequest:
    export_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    is_sensitive = extract_if_found(__data_sensitivity_pattern, text, lambda m: not m.group('sensitivity').lower().startswith('no'))
    destination = extract_if_found(__export_destination_pattern, text, lambda m: m.group('destination'))

    return DataExportRequest(export_reason, is_sensitive, destination)


def attempt_to_construct_devtool_install(text: str) -> DevToolInstallRequest:
    installation_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    team_leader_approval = extract_if_found(__approval_pattern, text, lambda m: m.group('approval'))
    return DevToolInstallRequest(installation_reason, team_leader_approval)


def attempt_to_construct_firewall_change(text: str) -> FireWallChangeRequest:
    firewall_change_source = extract_if_found(__firewall_source, text, lambda m: m.group('source'))
    firewall_change_destination = extract_if_found(__firewall_destination, text,
                                                   lambda m: f"{m.group('ip')}:{m.group('port')}")
    firewall_change_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    return FireWallChangeRequest(firewall_change_reason, firewall_change_source, firewall_change_destination)


def attempt_to_construct_network_access(text: str) -> NetworkAccessRequest:
    network_access_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    network_access_source = extract_if_found(__network_cidr_pattern, text, lambda m: m.group('ip'))
    is_sensitive = extract_if_found(__data_sensitivity_pattern, text,
                                    lambda m: not m.group('sensitivity').lower().startswith('no'))
    firewall_change_destination = extract_if_found(__firewall_destination, text,
                                                   lambda m: f"{m.group('ip')}:{m.group('port')}")
    return NetworkAccessRequest(network_access_reason, network_access_source, firewall_change_destination)


def attempt_to_construct_permissions_change(text: str) -> PermissionsChangeRequest:
    permissions_reason = extract_if_found(__request_justification_pattern, text, lambda m: m.group('justification'))
    duration = extract_if_found(__duration_pattern, text, lambda m: m.group('duration'))
    manager_approval = extract_if_found(__approval_pattern, text, lambda m: m.group('approval'))
    cloud_resource = extract_if_found(__cloud_resource_pattern, text, lambda m: m.group('cloud_resource'))
    role = extract_if_found(__access_role_pattern, text, lambda m: m.group('role'))

    return PermissionsChangeRequest(permissions_reason, duration, manager_approval, cloud_resource, role)


def attempt_to_construct_vendor_approval(text: str) -> VendorApprovalRequest:
    vendor_name = extract_if_found(__vendor_name_pattern, text, lambda m: m.group('vendor_name').strip())
    pii_involvement = extract_if_found(__pii_involvement_pattern, text, lambda m: m.group('pii_involvement').strip())
    vendor_security_questionnaire_result = extract_if_found(__vendor_security_questionnaire_pattern, text, lambda m: 'pass' in m.group('score').strip().lower())
    legal_review_status = extract_if_found(__legal_review_pattern, text, lambda m: all([negative_indication not in m.group(0).strip().lower() for negative_indication in ['don\'t', 'invalid']]))
    return VendorApprovalRequest(vendor_name, vendor_security_questionnaire_result, pii_involvement, legal_review_status)


__allow_traffic = re.compile(r'allow\s*\w*\s*traffic', flags=re.IGNORECASE)
__provide_services = re.compile(r'provides? (\w*\s*)+services', flags=re.IGNORECASE)

__firewall_preamble = re.compile(r'temporary firewall rule|allow ssh to external ip', flags=re.IGNORECASE)
__firewall_source = re.compile(r'from (?P<source>(\w+\s*)*)', flags=re.IGNORECASE)
__firewall_destination = re.compile(r'to (\w+\s+)*(?P<ip>(\d+\.){3}\d+) on port (?P<port>\d+)', flags=re.IGNORECASE)

__request_justification_pattern = re.compile(r'((for)|(to)) (?P<justification>(\w+\s*)+)(\.|$)', flags=re.IGNORECASE)

__data_sensitivity_pattern = re.compile(r'data classification: (?P<sensitivity>((\w|\.)+\s*)+|((no )?direct identifiers present))', flags=re.IGNORECASE)
__pii_involvement_pattern = re.compile(r'(?P<pii_involvement>((no )?(direct identifiers present|pii involve(d|ment))))', flags=re.IGNORECASE)

__duration_pattern = re.compile(r'(?P<duration>\d+\s*(days?|hours?|minutes?|seconds?))', flags=re.IGNORECASE)

__approval_pattern = re.compile(r'jira ticket: (?P<approval>\w+-\d+)', flags=re.IGNORECASE)
__export_destination_pattern = re.compile(r'export(ed)? to (\w+\s+)*(?P<destination>(\w+-)+\w+)', flags=re.IGNORECASE)

__cloud_resource_pattern = re.compile(r'aws account (?P<cloud_resource>(\w+-)+\w+)', flags=re.IGNORECASE)
__access_role_pattern = re.compile(r'requesting (?P<role>\w+) role', flags=re.IGNORECASE)

__network_cidr_pattern = re.compile(r'from (internal subnet )?(?P<ip>(\d+\.){3}\d+/\d+)', flags=re.IGNORECASE)

__vendor_name_pattern = re.compile(r'(?P<vendor_name>((\w|,)+\s+)+)provide', flags=re.IGNORECASE)
__vendor_security_questionnaire_pattern = re.compile(r'questionnaire with a (?P<score>(\w)+\s*) score', flags=re.IGNORECASE)
__legal_review_pattern = re.compile(r'(don\'t )?have a(n in| )valid soc (2|II) type (2|II) report', flags=re.IGNORECASE)