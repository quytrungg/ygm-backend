from rest_framework.exceptions import ValidationError


class NonFieldValidationError(ValidationError):
    """Wrap ValidationError class to pass `non_field_errors`.

    We often need to raise a ValidationError outside of serializer and pass non
    field errors. To simplify call of the non field validation error, pass a
    dict into init of super class with the key "non_field_errors" and a list
    with the error message as the value.

    """

    def __init__(self, message: str | list):
        if not isinstance(message, list):
            message = [message]
        super().__init__(
            detail={"non_field_errors": message},
        )
