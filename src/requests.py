from abc import ABC


class UserRequest(ABC):
    def _get_mandatory_fields(self):
        return []

    def is_valid(self) -> bool:
        return None not in self._get_mandatory_fields()


class UnIdentifiedUserRequest(UserRequest):
    def is_valid(self) -> bool:
        return False


class CloudResourceAccessRequest(UserRequest):
    def __init__(self, business_justification: str, sensitivity: str):
        super().__init__()
        self.business_justification = business_justification
        self.sensitivity = sensitivity

    def _get_mandatory_fields(self):
        return [self.business_justification, self.sensitivity]


class DataExportRequest(UserRequest):
    def __init__(self, business_justification: str, PII_involvment:bool, destination: str):
        super().__init__()
        self.business_justification = business_justification
        self.PII_involvement = PII_involvment
        self.destination = destination

    def _get_mandatory_fields(self):
        return [self.business_justification, self.PII_involvement, self.destination]


class DevToolInstallRequest(UserRequest):
    def __init__(self, business_justification: str, team_leader_approval: str):
        super().__init__()
        self.business_justification = business_justification
        self.team_leader_approval = team_leader_approval

    def _get_mandatory_fields(self):
        return [self.business_justification, self.team_leader_approval]


class FireWallChangeRequest(UserRequest):
    def __init__(self, business_justification, source_system, destination_ip):
        super().__init__()
        self.business_justification = business_justification
        self.source_system = source_system
        self.destination_ip = destination_ip

    def _get_mandatory_fields(self):
        return [self.business_justification, self.source_system, self.destination_ip]


class PermissionsChangeRequest(UserRequest):
    def __init__(self, business_justification: str, duration: str, manager_approval: str):
        super().__init__()
        self.business_justification = business_justification
        self.duraction = duration
        self.manager_approval = manager_approval

    def _get_mandatory_fields(self):
        return [self.business_justification, self.duraction, self.manager_approval]
