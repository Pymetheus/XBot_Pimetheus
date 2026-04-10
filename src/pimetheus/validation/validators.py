from typing import Any, TypeVar

import structlog
from pydantic import BaseModel, ValidationError

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class SchemaValidator[T: BaseModel]:
    """
    Validate payloads against a Pydantic schema.

    Attributes:
        schema (type[T]): The Pydantic model used for validation.
        payload (Any): The raw data to validate.
    """

    def __init__(self, schema: type[T], payload: Any) -> None:
        self.schema = schema
        self.payload = payload

    def validate_payload(self) -> T:
        """
        Validate the payload using the provided schema.

        Returns:
            T: Validated Pydantic model instance.

        Raises:
            ValidationError: If the payload does not conform to the schema.
        """

        try:
            validated_payload = self.schema.model_validate(self.payload)
            logger.info("Payload validated successfully", schema=self.schema.__name__)
            return validated_payload
        except ValidationError:
            logger.exception("Failed to validate payload", schema=self.schema.__name__)
            raise
