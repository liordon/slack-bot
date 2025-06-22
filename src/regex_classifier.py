import re

from typing import Callable, Any

from src.requests import *
from src.constants import *

allow_traffic = re.compile(r'allow\s*\w*\s*traffic')
provide_services = re.compile(r'provides? (\w*\s*)+services')

firewall_preamble = re.compile(r'Requesting temporary firewall rule to allow outbound SSH ')
firewall_source = re.compile(r'from (?P<source>(\w+\s*)*)')
firewall_destination = re.compile(r'to (\w+\s+)*(?P<ip>(\d+\.){3}\d+) on port (?P<port>\d+)')
request_justification_pattern = re.compile(r'((for)|(to)) (?P<justification>(\w+\s*)+)')
data_sensitivity_pattern = re.compile(r'Data classification: (?P<sensitivity>((\w|\.)+\s*)+|((no )?direct identifiers present))')
duration_pattern = re.compile(r'(?P<duration>\d+\s*(days?|hours?|minutes?|seconds?))')
approval_pattern = re.compile(r'Jira ticket: (?P<approval>\w+-\d+)')
export_destination_pattern = re.compile(r'export to (?P<ip>(\w+\s*)+)')

def attempt_to_classify(text: str) -> str:
    if 'firewall' in text:
        return RequestTypes.FIREWALL_CHANGE
    if 'install' in text:
        return RequestTypes.DEVTOOL_INSTALL
    if 'role' in text:
        return RequestTypes.PERMISSION_CHANGE
    if 'export' in text:
        return RequestTypes.DATA_EXPORT
    if 'access' in text.lower():
        return RequestTypes.CLOUD_ACCESS
    if allow_traffic.search(text):
        return RequestTypes.NETWORK_ACCESS
    if provide_services.search(text):
        return RequestTypes.VENDOR_APPROVAL
    return RequestTypes.UNKNOWN

def extract_if_found(match: re.Match, extractor: Callable[[re.Match], Any]) -> Any:
    if match is not None:
        return extractor(match)
    else:
        return None

def attempt_to_construct_cloud_access(text: str) -> CloudResourceAccessRequest:
    access_reason = extract_if_found(request_justification_pattern.search(text), lambda m: m.group('justification'))
    sensitivity = extract_if_found(data_sensitivity_pattern.search(text), lambda m: m.group('sensitivity'))
    return CloudResourceAccessRequest(access_reason, sensitivity)

def attempt_to_construct_data_export(text: str) -> DataExportRequest:
    export_reason = extract_if_found(request_justification_pattern.search(text), lambda m: m.group('justification'))
    is_sensitive = extract_if_found(data_sensitivity_pattern.search(text), lambda m: not m.group('sensitivity').lower().startswith('no'))
    destination = extract_if_found(export_destination_pattern.search(text), lambda m: m.group('destination'))
    return DataExportRequest(export_reason, is_sensitive, destination)

def attempt_to_construct_devtool_install(text: str) -> DevToolInstallRequest:
    installation_reason = extract_if_found(request_justification_pattern.search(text), lambda m: m.group('justification'))
    team_leader_approval = extract_if_found(approval_pattern.search(text), lambda m: m.group('approval'))
    return DevToolInstallRequest(installation_reason, team_leader_approval)

def attempt_to_construct_firewall_change(text: str) -> FireWallChangeRequest:
    firewall_change_source = extract_if_found(firewall_source.search(text), lambda m: m.group('source'))
    firewall_change_destination = extract_if_found(firewall_destination.search(text),
                                                   lambda m: f"{m.group('ip')}:{m.group('port')}")
    firewall_change_reason = extract_if_found(request_justification_pattern.search(text), lambda m: m.group('justification'))
    return FireWallChangeRequest(firewall_change_reason, firewall_change_source, firewall_change_destination)

def attempt_to_construct_permissions_change(text: str) -> PermissionsChangeRequest:
    permissions_reason = extract_if_found(request_justification_pattern.search(text), lambda m: m.group('justification'))
    duration = extract_if_found(duration_pattern.search(text), lambda m: m.group('duration'))
    manager_approval = extract_if_found(approval_pattern.search(text), lambda m: m.group('approval'))
    return PermissionsChangeRequest(permissions_reason, duration, manager_approval)