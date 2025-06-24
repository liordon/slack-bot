from abc import ABC, abstractmethod
from typing import List, Any, Dict

from src.parsing.fields import RequestField


class UserRequest(ABC):

    def __init__(self, field_details: Dict[str, RequestField]):
        self._field_details = field_details

    def _get_mandatory_fields(self) -> List[RequestField]:
        """:returns a list with the values of all the mandatory fields for this request, whatever they are"""
        return [field for _, field in self._field_details.items() if field.is_required]

    def is_valid(self) -> bool:
        return None not in [getattr(self, field.name) for field in self._get_mandatory_fields()]

    def get_missing_fields(self) -> List[RequestField]:
        """:returns a list of missing fields for this request."""
        return [field for name, field in self._field_details.items() if getattr(self, name) is None]

    def pretty_print(self) -> str:
        formatted_fields = '\n\t' + '\n\t'.join([self._pretty_print_field(f) for f in (self._field_details.values())])
        return f"{self.__class__.__name__}\n{formatted_fields}"

    def _get_all_fields(self):
        return [m for m in dir(self) if not m.startswith("_") and not callable(getattr(self, m))]

    def _pretty_print_field(self, field: RequestField) -> str:
        return f"*<{field.name.replace('_', ' ')}>*: " + (
            'mandatory' if field.is_required else '_optional_'
        ) + f"\n{field.description}"


class UnIdentifiedUserRequest(UserRequest):
    def get_missing_fields(self) -> List[RequestField]:
        return []

    def _get_mandatory_fields(self):
        return []

    def is_valid(self) -> bool:
        return False


class CloudResourceAccessRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="sensitivity",
            description="A description of how sensitive is the data being accessed.",
            is_required=True
        )]

    def __init__(self, business_justification: str, sensitivity: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.sensitivity = sensitivity

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.sensitivity]

    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.sensitivity is None:
    #         missing_fields.append(RequestField(
    #             name="sensitivity",
    #             description="A description of how sensitive is the data being accessed.",
    #             is_required=True
    #         ))
    #     return missing_fields


class DataExportRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="PII_involvement",
            description="An indication whether personal identifiable customer data is being accessed.",
            is_required=True
        ),
        RequestField(
            name="destination",
            description="Where the data should be exported.",
            is_required=True
        )]

    def __init__(self, business_justification: str, PII_involvment: bool, destination: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.PII_involvement = PII_involvment
        self.destination = destination

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.PII_involvement, self.destination]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.PII_involvement is None:
    #         missing_fields.append(RequestField(
    #             name="PII_involvement",
    #             description="An indication whether personal identifiable customer data is being accessed.",
    #             is_required=True
    #         ))
    #     if self.destination is None:
    #         missing_fields.append(RequestField(
    #             name="destination",
    #             description="Where the data should be exported.",
    #             is_required=True
    #         ))
    #     return missing_fields


class DevToolInstallRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="team_leader_approval",
            description="A jira ticket listing your team leader's approval of this request.",
            is_required=True
        )
    ]

    def __init__(self, business_justification: str, team_leader_approval: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.team_leader_approval = team_leader_approval

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.team_leader_approval]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.team_leader_approval is None:
    #         missing_fields.append(RequestField(
    #             name="team_leader_approval",
    #             description="A jira ticket listing your team leader's approval of this request.",
    #             is_required=True
    #         ))
    #     return missing_fields


class FireWallChangeRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="source_system",
            description="The system for which network access should be granted.",
            is_required=True
        ),
        RequestField(
            name="destination_ip",
            description="The IP address which the system needs to access and on port which we intend to communicate with it.",
            is_required=True
        )
    ]

    def __init__(self, business_justification, source_system, destination_ip):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.source_system = source_system
        self.destination_ip = destination_ip

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.source_system, self.destination_ip]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.source_system is None:
    #         missing_fields.append(RequestField(
    #             name="source_system",
    #             description="The system for which network access should be granted.",
    #             is_required=True
    #         ))
    #     if self.destination_ip is None:
    #         missing_fields.append(RequestField(
    #             name="destination_ip",
    #             description="The IP address which the system needs to access and on port which we intend to communicate with it.",
    #             is_required=True
    #         ))
    #     return missing_fields


class NetworkAccessRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="source_cidr",
            description="The Classless Inter-Domain Routing (AKA IP segment) which requires network access.",
            is_required=True
        ),
        RequestField(
            name="engineering_approval",
            description="A jira ticket listing the engineering team's approval of this request.",
            is_required=True
        )
    ]

    def __init__(self, business_justification, source_cidr, engineering_approval):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.source_cidr = source_cidr
        self.engineering_approval = engineering_approval

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.source_cidr, self.engineering_approval]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.source_cidr is None:
    #         missing_fields.append(RequestField(
    #             name="source_cidr",
    #             description="The Classless Inter-Domain Routing (AKA IP segment) which requires network access.",
    #             is_required=True
    #         ))
    #     if self.engineering_approval is None:
    #         missing_fields.append(RequestField(
    #             name="engineering_approval",
    #             description="A jira ticket listing the engineering team's approval of this request.",
    #             is_required=True
    #         ))
    #     return missing_fields


class PermissionsChangeRequest(UserRequest):
    __fields = [
        RequestField(
            name="business_justification",
            description="The reason for this request.",
            is_required=True
        ),
        RequestField(
            name="duration",
            description="How long should access be granted.",
            is_required=True
        ),
        RequestField(
            name="manager_approval",
            description="A jira ticket listing your manager's approval of this request.",
            is_required=True
        ),
        RequestField(
            name="aws_account",
            description="the AWS account to which permissions should be changed.",
            is_required=False
        ),
        RequestField(
            name="role_requested",
            description="The role which should temporarily be granted.",
            is_required=False
        )
    ]

    def __init__(self, business_justification: str, duration: str, manager_approval: str, aws_account: str,
                 role_requested: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.duration = duration
        self.manager_approval = manager_approval
        self.aws_account = aws_account
        self.role_requested = role_requested

    # def _get_mandatory_fields(self):
    #     return [self.business_justification, self.duration, self.manager_approval]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.business_justification is None:
    #         missing_fields.append(RequestField(
    #             name="business_justification",
    #             description="The reason for this request.",
    #             is_required=True
    #         ))
    #     if self.duration is None:
    #         missing_fields.append(RequestField(
    #             name="duration",
    #             description="How long should access be granted.",
    #             is_required=True
    #         ))
    #     if self.manager_approval is None:
    #         missing_fields.append(RequestField(
    #             name="manager_approval",
    #             description="A jira ticket listing your manager's approval of this request.",
    #             is_required=True
    #         ))
    #     if self.aws_account is None:
    #         missing_fields.append(RequestField(
    #             name="aws_account",
    #             description="the AWS account to which permissions should be changed.",
    #             is_required=False
    #         ))
    #     if self.role_requested is None:
    #         missing_fields.append(RequestField(
    #             name="role_requested",
    #             description="The role which should temporarily be granted.",
    #             is_required=False
    #         ))
    #     return missing_fields


class VendorApprovalRequest(UserRequest):
    __fields = [
        RequestField(
            name="vendor_name",
            description="The vendor which requires onboarding.",
            is_required=False
        ),
        RequestField(
            name="security_questionnaire_completed",
            description="An indication whether said vendor completed our security questionnaire.",
            is_required=True
        ),
        RequestField(
            name="data_classification",
            description="A description of how sensitive is the data being accessed.",
            is_required=True
        ),
        RequestField(
            name="legal_review_completed",
            description="An indication that the company passed the required legal review.",
            is_required=True
        )
    ]

    def __init__(self, vendor_name: str, security_questionnaire_completed: bool, data_classification: str,
                 legal_review_completed: bool):
        super().__init__({f.name: f for f in self.__fields})
        self.vendor_name = vendor_name
        self.security_questionnaire_completed = security_questionnaire_completed
        self.data_classification = data_classification
        self.legal_review_completed = legal_review_completed

    # def _get_mandatory_fields(self):
    #     return [self.security_questionnaire_completed, self.data_classification, self.legal_review_completed]
    #
    # def get_missing_fields(self) -> List[RequestField]:
    #     missing_fields = []
    #     if self.vendor_name is None:
    #         missing_fields.append(RequestField(
    #             name="vendor_name",
    #             description="The vendor which requires onboarding.",
    #             is_required=False
    #         ))
    #     if self.security_questionnaire_completed is None:
    #         missing_fields.append(RequestField(
    #             name="security_questionnaire_completed",
    #             description="An indication whether said vendor completed our security questionnaire.",
    #             is_required=True
    #         ))
    #     if self.data_classification is None:
    #         missing_fields.append(RequestField(
    #             name="data_classification",
    #             description="A description of how sensitive is the data being accessed.",
    #             is_required=True
    #         ))
    #     if self.legal_review_completed is None:
    #         missing_fields.append(RequestField(
    #             name="legal_review_completed",
    #             description="An indication that the company passed the required legal review.",
    #             is_required=True
    #         ))
    #     return missing_fields


class RequestTypes(object):
    UNKNOWN = 'UNKNOWN'
    FIREWALL_CHANGE = 'FIREWALL CHANGE'
    DEVTOOL_INSTALL = 'DEVTOOL INSTALL'
    PERMISSION_CHANGE = 'PERMISSION CHANGE'
    DATA_EXPORT = 'DATA EXPORT'
    CLOUD_ACCESS = 'CLOUD RESOURCE ACCESS'
    NETWORK_ACCESS = 'NETWORK ACCESS'
    VENDOR_APPROVAL = 'VENDOR APPROVAL'
