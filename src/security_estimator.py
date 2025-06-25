import math

from src.parsing.constants import RequestTypes
from src.parsing.requests import (
    UserRequest, CloudResourceAccessRequest, DataExportRequest,
    NetworkAccessRequest, DevToolInstallRequest, FireWallChangeRequest, VendorApprovalRequest,
    PermissionsChangeRequest
)


# noinspection PyTypeChecker
def calculate_security_risk(request: UserRequest) -> int:
    if not request.is_valid():
        return 100
    req_type = request.request_type
    if req_type == RequestTypes.CLOUD_ACCESS:
        return _calculate_cloud_access_risk(request)
    elif req_type == RequestTypes.DATA_EXPORT:
        return _calculate_data_export_risk(request)
    elif req_type == RequestTypes.DEVTOOL_INSTALL:
        return _calculate_devtool_install_risk(request)
    elif req_type == RequestTypes.FIREWALL_CHANGE:
        return _calculate_firewall_change_risk(request)
    elif req_type == RequestTypes.NETWORK_ACCESS:
        return _calculate_network_access_risk(request)
    elif req_type == RequestTypes.PERMISSION_CHANGE:
        return _calculate_permissions_change_risk(request)
    elif req_type == RequestTypes.VENDOR_APPROVAL:
        return _calculate_vendor_approval_risk(request)
    else:
        return 100

def _calculate_cloud_access_risk(request: CloudResourceAccessRequest) -> int:
    score = 55
    if request.sensitivity is not None and 'high' in request.sensitivity.lower():
        score += 10
    return score

def _calculate_data_export_risk(request: DataExportRequest) -> int:
    score = 60
    if request.PII_involvement:
        score += 30
    if 'external' in request.destination.lower():
        score += 10
    return score

def _calculate_devtool_install_risk(request: DevToolInstallRequest) -> int:
    score = 35
    if 'performance' in request.business_justification.lower():
        score += 10
    return score

def _calculate_firewall_change_risk(request: FireWallChangeRequest) -> int:
    score = 65
    if 'third party' in request.business_justification.lower():
        score += 10
    if request.destination_ip.split(':')[-1] != '22':
        score += 10
    if request.destination_ip.split(':')[-1] == '443':
        score += 10
    return score

def _calculate_network_access_risk(request: NetworkAccessRequest) -> int:
    score = 65
    subnet_size_estimation = int(request.source_cidr.split('/')[-1])
    score += subnet_size_estimation
    return score

def _calculate_permissions_change_risk(request: PermissionsChangeRequest) -> int:
    score = 75
    permissions_change_duration = request.get_duration_in_hours()
    if math.isinf(permissions_change_duration):
        score += 20
    else:
        score += min(math.log(permissions_change_duration), 20)
    if request.aws_account is not None and 'prod' in request.aws_account.lower():
        score += 10
    return min(score, 100)

def _calculate_vendor_approval_risk(request: VendorApprovalRequest) -> int:
    score = 45
    if not request.security_questionnaire_completed:
        score += 20
    if not request.legal_review_completed:
        score += 10
    if 'confidential' in request.data_classification.lower():
        score += 15
    return min(score, 100)