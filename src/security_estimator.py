from src.parsing.requests import *


def calculate_security_risk(request: UserRequest) -> float:
    if not request.is_valid():
        return 100
    return 50
