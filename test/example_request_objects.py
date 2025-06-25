"""
Empty and filled requests used for tests. Generated via gemini.
"""
from src.parsing.requests import (
    UnIdentifiedUserRequest, CloudResourceAccessRequest,
    DataExportRequest, DevToolInstallRequest, FireWallChangeRequest, NetworkAccessRequest,
    PermissionsChangeRequest, VendorApprovalRequest
)

empty_unidentified = UnIdentifiedUserRequest()

empty_cloud_access = CloudResourceAccessRequest(None, None)

filled_cloud_access_1 = CloudResourceAccessRequest(
    "Access S3 bucket for Q3 financial reporting",
    "High"
)

filled_cloud_access_2 = CloudResourceAccessRequest(
    "Retrieve logs for debugging application performance",
    "Low"
)

empty_data_export = DataExportRequest(None, None, None)

filled_data_export_1 = DataExportRequest(
    "Export customer data for external marketing campaign",
    True,
    "External SFTP server (partner.com)"
)

filled_data_export_2 = DataExportRequest(
    "Internal data analysis for product improvement",
    False,
    "Internal data warehouse"
)

empty_devtool_install = DevToolInstallRequest(None, None)

filled_devtool_install_1 = DevToolInstallRequest(
    "Install custom IDE plugin for development workflow",
    "JIRA-DEV-54321"
)

filled_devtool_install_2 = DevToolInstallRequest(
    "Request for new performance monitoring tool",
    "JIRA-DEV-98765"
)

empty_firewall_change = FireWallChangeRequest(None, None, None)

filled_firewall_change_1 = FireWallChangeRequest(
    "Allow inbound traffic from new partner VPN",
    "Partner VPN Gateway",
    "203.0.113.10:8080"
)

filled_firewall_change_2 = FireWallChangeRequest(
    "Enable outbound access to third-party analytics service",
    "Application Server Cluster",
    "198.51.100.20:443"
)

empty_network_access = NetworkAccessRequest(None, None, None)

filled_network_access_1 = NetworkAccessRequest(
    "Grant access for new microservice deployment",
    "10.0.1.0/24",
    "JIRA-ENG-NET-001"
)

filled_network_access_2 = NetworkAccessRequest(
    "Allow testing environment connectivity for QA team",
    "172.16.5.0/28",
    "JIRA-ENG-NET-002"
)

empty_permissions_change = PermissionsChangeRequest(None, None, None, None, None)

filled_permissions_change_1 = PermissionsChangeRequest(
    "Grant temporary S3 write access for data migration",
    "48 hours",
    "JIRA-MGR-001",
    "production-data-bucket",
    "S3WriteRole"
)

filled_permissions_change_2 = PermissionsChangeRequest(
    "Adjust IAM role for new developer",
    "Indefinite",
    "JIRA-MGR-002",
    None,  # AWS account not specified
    "DeveloperReadOnly"
)

empty_vendor_approval = VendorApprovalRequest(None, None, None, None)

filled_vendor_approval_1 = VendorApprovalRequest(
    "Data Analytics Pro Inc.",
    True,
    "Confidential Customer Data",
    True
)

filled_vendor_approval_2 = VendorApprovalRequest(
    None,
    False,
    "Publicly Available Data",
    True
)

ALL_EMPTY_REQUESTS = [
    empty_unidentified,
    empty_cloud_access,
    empty_data_export,
    empty_devtool_install,
    empty_firewall_change,
    empty_network_access,
    empty_permissions_change,
    empty_vendor_approval,
]


FILLED_REQUESTS = [
    filled_cloud_access_1,
    filled_data_export_1,
    filled_devtool_install_1,
    filled_firewall_change_1,
    filled_network_access_1,
    filled_permissions_change_1,
    filled_vendor_approval_1,
]


ALTERNATE_FILLED_REQUESTS = [
    filled_cloud_access_2,
    filled_data_export_2,
    filled_devtool_install_2,
    filled_firewall_change_2,
    filled_network_access_2,
    filled_permissions_change_2,
    filled_vendor_approval_2,
]