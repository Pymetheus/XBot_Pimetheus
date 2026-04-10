from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pimetheus")
except PackageNotFoundError:
    __version__ = "unknown"
