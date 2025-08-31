from sqlalchemy import Column, String
from sqlalchemy.orm import declared_attr


class Parameter:
    """
    SQLAlchemy mixin for models with a name and value.
    """

    @declared_attr
    def name(cls):
        return Column(String)

    @declared_attr
    def value(cls):
        return Column(String)