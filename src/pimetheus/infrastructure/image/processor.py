import io
from pathlib import Path

import structlog
from PIL import Image

from pimetheus.infrastructure.image.exceptions import ImageProcessingError
from pimetheus.infrastructure.storage.paths import PathManager, ProjectPaths

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class ImageProcessor:
    """
    Resize and compress images to a target file size.

    Attributes:
        TARGET_SIZE_KB (int): Default max file size in KB.
        MAX_DIMENSION (int): Max width/height in pixels.
        QUALITY_COMPRESSION_STEP (int): JPEG quality decrement step.
    """

    TARGET_SIZE_KB = 1024
    MAX_DIMENSION = 2560
    QUALITY_COMPRESSION_STEP = 1

    def __init__(self, filename: str, path: Path | None = None) -> None:
        """
        Initialize the ImageProcessor.

        Args:
            filename: Name of the image file to process.
            path: Optional path to the raw image directory. If not provided,
                  the default raw directory defined in ProjectPaths is used.
        """

        self.raw_path = path or ProjectPaths.RAW
        self.filename = filename
        self.filepath = PathManager(self.raw_path / self.filename).resolve_file_path()
        self.processed_path = ProjectPaths.PROCESSED

    def get_image_size_kb(self) -> float:
        """
        Return image file size in kilobytes.

        Returns:
            float: File size in KB, or 0 if file is empty.

        Raises:
            OSError: If file metadata cannot be accessed.
        """

        file_size_bytes = self.filepath.stat().st_size

        if file_size_bytes == 0:
            logger.error("Empty image", path=self.filepath, size=file_size_bytes)
            return 0

        file_size_kb = file_size_bytes / 1024

        logger.info("Getting image size", path=self.filepath, size=file_size_kb)
        return file_size_kb

    def compress_to_target(self, target_size_kb: int | None = None) -> Path:
        """
        Resize and compress image to target size in KB.

        Parameters:
            target_size_kb (int | None): Max file size in KB.

        Returns:
            Path: Path to compressed image.

        Raises:
            ImageProcessingError: If processing fails or target size is not reached.
            OSError: If file cannot be read or written.
        """

        try:
            original_size_kb = self.get_image_size_kb()
            file_size_kb = 0.0
            target_size_kb = target_size_kb or self.TARGET_SIZE_KB

            if original_size_kb == 0:
                logger.error("Unable to compress empty image", path=self.filepath, size=original_size_kb)
                raise ImageProcessingError("Image file is empty")

            logger.info("Processing image", path=self.filepath, size=original_size_kb, target_size=target_size_kb)

            with Image.open(self.filepath) as img:
                logger.info("Original dimensions", width=img.size[0], height=img.size[1], size=original_size_kb)

                buffer = io.BytesIO()
                quality = 100
                img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)

                while quality > 0:
                    buffer.seek(0)
                    buffer.truncate()

                    img.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)
                    file_size_kb = buffer.tell() / 1024
                    logger.info("Compressing image", size=file_size_kb, quality=quality)

                    if file_size_kb <= target_size_kb:
                        break
                    quality -= self.QUALITY_COMPRESSION_STEP

                if quality == 0:
                    logger.error(
                        "Unable to compress image to target size",
                        path=self.filepath,
                        size=file_size_kb,
                        quality=quality,
                        target_size=target_size_kb,
                    )
                    raise ImageProcessingError("Compression target not reached")

                output_path = self.processed_path / self.filename
                img.save(output_path, format="JPEG", quality=quality, optimize=True, progressive=True)

            logger.info("Saved compressed image", path=output_path, size=file_size_kb)
            return output_path

        except OSError as e:
            logger.error("Failed to read/write image", path=self.filepath)
            raise ImageProcessingError(f"Cannot process image file: {self.filepath}") from e
