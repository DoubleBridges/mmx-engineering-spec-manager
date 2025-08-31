from sqlalchemy import Column, String
from sqlalchemy.orm import declared_attr

class CalloutMixin:
    """
    SQLAlchemy mixin for models that contain callout attributes.
    """
    @declared_attr
    def material(cls):
        return Column(String)

    @declared_attr
    def tag(cls):
        return Column(String)

    @declared_attr
    def description(cls):
        return Column(String)