
class RequestField(object):
    def __init__(self, name: str, description: str, is_required: bool):
        self.name = name
        self.description = description
        self.is_required = is_required