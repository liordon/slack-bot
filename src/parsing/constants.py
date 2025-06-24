"""
Lists various constant values in one place
"""
from enum import Enum


class RequestFollowUp(Enum):
    """
    Followup strategies we may employ for a given requests.
    """
    ACCEPT = 'accept'
    REJECT = 'reject'
    REQUEST_FURTHER_DETAILS = 'request_further_details'
    IRRELEVANT = 'irrelevant'


class RequestTypes(object):
    """String names for every kind of security request."""
    UNKNOWN = 'UNKNOWN'
    FIREWALL_CHANGE = 'FIREWALL CHANGE'
    DEVTOOL_INSTALL = 'DEVTOOL INSTALL'
    PERMISSION_CHANGE = 'PERMISSION CHANGE'
    DATA_EXPORT = 'DATA EXPORT'
    CLOUD_ACCESS = 'CLOUD RESOURCE ACCESS'
    NETWORK_ACCESS = 'NETWORK ACCESS'
    VENDOR_APPROVAL = 'VENDOR APPROVAL'
