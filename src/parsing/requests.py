"""
Details generic security requests and their specific implementations.
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List, Dict
import math

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

    def get_mandatory_fields(self) -> List[RequestField]:
        """:returns a list with the values of all the mandatory fields for this request, whatever they are"""
        return [field for _, field in self._field_details.items() if field.is_required]

    def is_valid(self) -> bool:
        """:returns True if all mandatory fields are filled."""
        return None not in [getattr(self, field.name) for field in self.get_mandatory_fields()]

    def get_missing_fields(self) -> List[RequestField]:
        """:returns a list of missing fields for this request."""
        return [field for name, field in self._field_details.items() if getattr(self, name) is None]

    def pretty_print_description(self) -> str:
        """prints a legible description of the request."""
        formatted_fields = '\n\t' + '\n\t'.join(
            [self._pretty_print_field_description(f) for f in (self._field_details.values())]
        )
        return f"{self.__class__.__name__}\n{formatted_fields}"

    def pretty_print_content(self) -> str:
        """prints a legible description of the request."""
        formatted_fields = '\n\t' + '\n\t'.join(
            [self._pretty_print_field_content(f) for f in (self._field_details.values())]
        )
        return f"{self.__class__.__name__}\n{formatted_fields}"

    @staticmethod
    def _pretty_print_field_description(field: RequestField) -> str:
        return f"*<{field.name.replace('_', ' ')}>*: " + (
            'mandatory' if field.is_required else '_optional_'
        ) + f"\n{field.description}"

    def _pretty_print_field_content(self, field: RequestField) -> str:
        field_value = getattr(self, field.name)
        return f"*<{field.name.replace('_', ' ')}>* (" + (
            'mandatory' if field.is_required else '_optional_'
        ) + f"): " + (
            str(field_value) if field_value is not None else "_<empty>_"
        )

    @abstractmethod
    def merge_with(self, new_request: 'UserRequest') -> 'UserRequest':
        if not isinstance(new_request, self.__class__):
            raise TypeError(
                f"can only merge of the same type, but you tried to merge a {self.__class__} with a {new_request.__class__}"
            )
        return new_request


    @property
    def request_type(self) -> str:
        return RequestTypes.UNKNOWN

class UnIdentifiedUserRequest(UserRequest):
    def __init__(self):
        super().__init__({})

    @property
    def request_type(self) -> str:
        return RequestTypes.UNKNOWN

    def get_missing_fields(self) -> List[RequestField]:
        return []

    def get_mandatory_fields(self):
        return []

    def is_valid(self) -> bool:
        return False

    def merge_with(self, new_request: 'UserRequest') -> 'UserRequest':
        super().merge_with(new_request)
        return new_request

    def __eq__(self, other):
        return isinstance(other, UnIdentifiedUserRequest)


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

    def merge_with(self, new_request: 'CloudResourceAccessRequest') -> 'CloudResourceAccessRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.sensitivity is not None:
            merged_request.sensitivity = new_request.sensitivity
        return merged_request

    def __eq__(self, other: 'CloudResourceAccessRequest') -> bool:
        return (
            isinstance(other, CloudResourceAccessRequest)
            and self.business_justification == other.business_justification
            and self.sensitivity == other.sensitivity
        )

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

    def merge_with(self, new_request: 'DataExportRequest') -> 'DataExportRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.PII_involvement is not None:
            merged_request.PII_involvement = new_request.PII_involvement
        if new_request.destination is not None:
            merged_request.destination = new_request.destination
        return merged_request

    def __eq__(self, other: 'DataExportRequest') -> bool:
        return (
            isinstance(other, DataExportRequest)
            and self.business_justification == other.business_justification
            and self.PII_involvement == other.PII_involvement
            and self.destination == other.destination
        )


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

    def merge_with(self, new_request: 'DevToolInstallRequest') -> 'DevToolInstallRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.team_leader_approval is not None:
            merged_request.team_leader_approval = new_request.team_leader_approval
        return merged_request

    def __eq__(self, other: 'DevToolInstallRequest') -> bool:
        return (
                isinstance(other, DevToolInstallRequest)
                and self.business_justification == other.business_justification
                and self.team_leader_approval == other.team_leader_approval
        )


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

    def merge_with(self, new_request: 'FireWallChangeRequest') -> 'FireWallChangeRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.source_system is not None:
            merged_request.source_system = new_request.source_system
        if new_request.destination_ip is not None:
            merged_request.destination_ip = new_request.destination_ip
        return merged_request

    def __eq__(self, other: 'FireWallChangeRequest') -> bool:
        return (
                isinstance(other, FireWallChangeRequest)
                and self.business_justification == other.business_justification
                and self.source_system == other.source_system
                and self.destination_ip == other.destination_ip
        )


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

    def merge_with(self, new_request: 'NetworkAccessRequest') -> 'NetworkAccessRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.source_cidr is not None:
            merged_request.source_cidr = new_request.source_cidr
        if new_request.engineering_approval is not None:
            merged_request.engineering_approval = new_request.engineering_approval
        return merged_request

    def __eq__(self, other: 'NetworkAccessRequest') -> bool:
        return (
            isinstance(other, NetworkAccessRequest)
            and self.business_justification == other.business_justification
            and self.source_cidr == other.source_cidr
            and self.engineering_approval == other.engineering_approval
        )


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

    def merge_with(self, new_request: 'PermissionsChangeRequest') -> 'PermissionsChangeRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.business_justification is not None:
            merged_request.business_justification = new_request.business_justification
        if new_request.duration is not None:
            merged_request.duration = new_request.duration
        if new_request.manager_approval is not None:
            merged_request.manager_approval = new_request.manager_approval
        if new_request.aws_account is not None:
            merged_request.aws_account = new_request.aws_account
        if new_request.role_requested is not None:
            merged_request.role_requested = new_request.role_requested
        return merged_request

    def __eq__(self, other: 'PermissionsChangeRequest') -> bool:
        return (
            isinstance(other, PermissionsChangeRequest)
            and self.business_justification == other.business_justification
            and self.duration == other.duration
            and self.manager_approval == other.manager_approval
            and self.aws_account == other.aws_account
            and self.role_requested == other.role_requested
        )

    def get_duration_in_hours(self) -> float:
        multiplier = math.inf
        if 'hour' in self.duration:
            multiplier = 1.
        elif 'day' in self.duration:
            multiplier = 24.
        elif 'minute' in self.duration:
            multiplier = 1. / 60
        elif 'second' in self.duration:
            multiplier = 1. / 3600
        else:
            return math.inf
        amount_of_units = int(self.duration.split(' ')[0])
        return amount_of_units * multiplier

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

    def merge_with(self, new_request: 'VendorApprovalRequest') -> 'VendorApprovalRequest':
        super().merge_with(new_request)
        merged_request = deepcopy(self)
        if new_request.vendor_name is not None:
            merged_request.vendor_name = new_request.vendor_name
        if new_request.security_questionnaire_completed is not None:
            merged_request.security_questionnaire_completed = new_request.security_questionnaire_completed
        if new_request.data_classification is not None:
            merged_request.data_classification = new_request.data_classification
        if new_request.legal_review_completed is not None:
            merged_request.legal_review_completed = new_request.legal_review_completed
        return merged_request

    def __eq__(self, other: 'VendorApprovalRequest') -> bool:
        return (
            isinstance(other, VendorApprovalRequest)
            and self.vendor_name == other.vendor_name
            and self.security_questionnaire_completed == other.security_questionnaire_completed
            and self.data_classification == other.data_classification
            and self.legal_review_completed == other.legal_review_completed
        )
