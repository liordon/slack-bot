from abc import ABC

class Attitude(ABC):
    def generate_acknowledgement_block(self, payload: dict) -> dict:
        pass

    def generate_rejection_block(self, payload: dict) -> dict:
        pass

    def generate_approval_block(self, payload: dict) -> dict:
        pass

    def generate_request_for_field(self, payload: dict, field: str, field_desc:str) -> dict:
        pass

    def generate_reflection_block(self, payload: dict) -> dict:
        request_lines = payload.get('text').split('\n')
        return wrap_with_markdown_block('>'+'\n>'.join(request_lines))

    def generate_initial_classification_block(self, classification: str) -> dict:
        pass

def wrap_with_markdown_block(txt: str) -> dict:
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": txt
        }
    }

def determine_indefinite_article(word: str) -> str:
    if word.lower()[0] in 'aeiouy':
        return 'an'
    else:
        return 'a'