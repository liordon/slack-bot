"""
Details generic security requests and their specific implementations.
"""
from abc import ABC
from typing import List, Dict

from src.parsing.constants import RequestTypes


class RequestField(object):
    """Describes a field in a request and its function."""

    def __init__(self, name: str, description: str, is_required: bool):
        self.name = name
        self.description = description
        self.is_required = is_required


class UserRequest(ABC):
    """A base class for all user security requests."""

    def __init__(self, field_details: Dict[str, RequestField]):
        self._field_details = field_details

    def _get_mandatory_fields(self) -> List[RequestField]:
        """:returns a list with the values of all the mandatory fields for this request, whatever they are"""
        return [field for _, field in self._field_details.items() if field.is_required]

    def is_valid(self) -> bool:
        """:returns True if all mandatory fields are filled."""
        return None not in [getattr(self, field.name) for field in self._get_mandatory_fields()]

    def get_missing_fields(self) -> List[RequestField]:
        """:returns a list of missing fields for this request."""
        return [field for name, field in self._field_details.items() if getattr(self, name) is None]

    def pretty_print(self) -> str:
        """prints a legible description of the request."""
        formatted_fields = '\n\t' + '\n\t'.join(
            [self._pretty_print_field(f) for f in (self._field_details.values())]
        )
        return f"{self.__class__.__name__}\n{formatted_fields}"

    @staticmethod
    def _pretty_print_field(field: RequestField) -> str:
        return f"*<{field.name.replace('_', ' ')}>*: " + (
            'mandatory' if field.is_required else '_optional_'
        ) + f"\n{field.description}"


class UnIdentifiedUserRequest(UserRequest):
    def __init__(self):
        super().__init__({})

    def get_missing_fields(self) -> List[RequestField]:
        return []

    def _get_mandatory_fields(self):
        return []

    def is_valid(self) -> bool:
        return False

    @property
    def request_type(self) -> str:
        return RequestTypes.UNKNOWN


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
        )
    ]

    def __init__(self, business_justification: str, sensitivity: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.sensitivity = sensitivity

    @property
    def request_type(self) -> str:
        return RequestTypes.CLOUD_ACCESS


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
        )
    ]

    def __init__(self, business_justification: str, PII_involvment: bool, destination: str):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.PII_involvement = PII_involvment
        self.destination = destination

        @property
        def request_type(self) -> str:
            return RequestTypes.DATA_EXPORT


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

    @property
    def request_type(self) -> str:
        return RequestTypes.DEVTOOL_INSTALL


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

    @property
    def request_type(self) -> str:
        return RequestTypes.FIREWALL_CHANGE


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

    @property
    def request_type(self) -> str:
        return RequestTypes.NETWORK_ACCESS


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

    def __init__(
            self, business_justification: str, duration: str, manager_approval: str,
            aws_account: str,
            role_requested: str
            ):
        super().__init__({f.name: f for f in self.__fields})
        self.business_justification = business_justification
        self.duration = duration
        self.manager_approval = manager_approval
        self.aws_account = aws_account
        self.role_requested = role_requested

    @property
    def request_type(self) -> str:
        return RequestTypes.PERMISSION_CHANGE


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

    def __init__(
            self, vendor_name: str, security_questionnaire_completed: bool,
            data_classification: str,
            legal_review_completed: bool
            ):
        super().__init__({f.name: f for f in self.__fields})
        self.vendor_name = vendor_name
        self.security_questionnaire_completed = security_questionnaire_completed
        self.data_classification = data_classification
        self.legal_review_completed = legal_review_completed

    @property
    def request_type(self) -> str:
        return RequestTypes.VENDOR_APPROVAL
