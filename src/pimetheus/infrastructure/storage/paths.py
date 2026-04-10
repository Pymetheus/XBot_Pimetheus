from pathlib import Path

import structlog

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class ProjectPaths:
    """
    Provide access to project directory paths.

    Attributes:
        ROOT (Path): Project root directory.
        DATA (Path): Data directory.
        CONFIG (Path): Config directory.
        RAW (Path): Raw data directory.
        PROCESSED (Path): Processed data directory.
        LOGS (Path): Logs directory.
    """

    ROOT = Path(__file__).resolve().parents[4]

    DATA = ROOT / "data"
    CONFIG = ROOT / ".config"
    RAW = DATA / "raw"
    PROCESSED = DATA / "processed"
    LOGS = ROOT / ".log"

    @classmethod
    def create_project_directories(cls) -> None:
        """
        Create required project directories.

        Returns:
            None

        Raises:
            OSError: If directory creation fails.
        """
        for path in [cls.DATA, cls.RAW, cls.PROCESSED, cls.LOGS]:
            path.mkdir(parents=True, exist_ok=True)
        logger.info("Created project directories")


class PathManager:
    """
    Ensure file paths exist.

    Attributes:
        path (Path): File path.
    """

    def __init__(self, path: Path | str) -> None:
        """
        Initialize the PathManager with a file path.
        """

        self.path: Path = Path(path)

    def resolve_file_path(self) -> Path:
        """
        Ensure file and parent directories exist.

        Returns:
            Path: Existing or newly created file path.

        Raises:
            OSError: If filesystem operations fail.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)

            if not self.path.exists():
                self.path.touch()
                logger.info("Created file path", path=self.path)
            return self.path
        except OSError:
            logger.exception("Failed to get file path", path=self.path)
            raise
