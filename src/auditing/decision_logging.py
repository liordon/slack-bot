from dataclasses import asdict

from src.auditing.bot_decision import BotDecision


class DecisionLogger(object):
    def __init__(self, log_path: str = 'logs/audit.log'):
        self.log_path = log_path

    def log(self, decision: BotDecision) -> None:
        with open(self.log_path, 'a') as file:
            file.write(str(asdict(decision)))
            file.write('\n')