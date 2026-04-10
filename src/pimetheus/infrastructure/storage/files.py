import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import structlog
from httpx import Response

from pimetheus.infrastructure.storage.paths import PathManager

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class FileStorage:
    """
    Handle file read/write operations for JSON and binary data.

    Attributes:
        path (Path): Base directory.
        filename (str): File name.
        filepath (Path): Resolved file path.
    """

    def __init__(self, path: Path, filename: str) -> None:
        """
        Initialize the FileStorage.
        """

        self.path = path
        self.filename = filename
        self.filepath = PathManager(self.path / self.filename).resolve_file_path()

    def read_json(self) -> Any:
        """
        Read JSON content from file.

        Returns:
            Any: Parsed JSON data, or empty dict if file is empty.

        Raises:
            json.JSONDecodeError: If JSON is invalid.
            OSError: If file cannot be read.
        """

        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                content = f.read()

                if not content.strip():
                    logger.warning("Empty file", path=self.filepath)
                    return {}

                data = json.loads(content)

            logger.info("Reading JSON file", path=self.filepath)
            return data

        except json.JSONDecodeError:
            logger.exception("Invalid JSON format", path=self.filepath)
            raise

        except OSError:
            logger.exception("Failed to read JSON file", path=self.filepath)
            raise

    def write_json(self, data: Mapping[str, Any]) -> Path:
        """
        Write JSON data to file.

        Parameters:
            data (Mapping[str, Any]): JSON-serializable data.

        Returns:
            Path: Path to written file.

        Raises:
            OSError: If file cannot be written.
            TypeError: If data is not JSON-serializable.
        """

        try:
            with self.filepath.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info("Writing JSON file", path=self.filepath)
            return self.filepath

        except OSError:
            logger.exception("Failed to write JSON file", path=self.filepath)
            raise

    def write_http_response(self, response: Response) -> Path:
        """
        Write HTTP response content to file.

        Parameters:
            response (Response): HTTP response object.

        Returns:
            Path: Path to written file.

        Raises:
            OSError: If file cannot be written.
        """

        try:
            if len(response.content) == 0:
                logger.warning("HTTP response content is empty", path=self.filepath)

            with self.filepath.open("wb") as f:
                f.write(response.content)
                logger.info("Saved HTTP response", path=self.filepath)
                return self.filepath

        except OSError:
            logger.exception("Failed to save HTTP response", path=self.filepath)
            raise

    def read_image_bytes(self) -> bytes:
        """
        Read binary data from file.

        Returns:
            bytes: File content.

        Raises:
            OSError: If file cannot be read.
        """

        try:
            with self.filepath.open("rb") as f:
                image_data = f.read()

            logger.info("Reading image bytes", path=self.filepath)
            return image_data

        except OSError:
            logger.exception("Failed to read image", path=self.filepath)
            raise
