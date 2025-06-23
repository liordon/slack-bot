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