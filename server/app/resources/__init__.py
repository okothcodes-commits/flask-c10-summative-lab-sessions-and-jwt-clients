from .auth import register_auth_resources
from .notes import register_note_resources


def register_resources(api):
    register_auth_resources(api)
    register_note_resources(api)
