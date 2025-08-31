from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, declared_attr

class PromptsMixin:
    """
    SQLAlchemy mixin for models that contain a collection of prompts.
    """
    @declared_attr
    def name(cls):
        return Column(String)

    @declared_attr
    def prompts(cls):
        return relationship("Prompt")