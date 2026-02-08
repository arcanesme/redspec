"""Custom exceptions for redspec."""


class RedspecError(Exception):
    """Base exception for all redspec errors."""


class IconNotFoundError(RedspecError):
    """Raised when an Azure icon cannot be resolved."""

    def __init__(self, resource_type: str) -> None:
        self.resource_type = resource_type
        super().__init__(f"No icon found for resource type: {resource_type}")


class ConnectionTargetNotFoundError(RedspecError):
    """Raised when a connection references a non-existent resource name."""

    def __init__(self, name: str, field: str = "target") -> None:
        self.name = name
        self.field = field
        super().__init__(
            f"Connection {field} '{name}' does not match any resource name"
        )


class DuplicateResourceNameError(RedspecError):
    """Raised when two resources share the same name."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Duplicate resource name: '{name}'")


class IconPackDownloadError(RedspecError):
    """Raised when the Azure icon pack cannot be downloaded."""


class IconPackNotFoundError(RedspecError):
    """Raised when a YAML references an unknown or uninstalled icon pack."""

    def __init__(self, pack_name: str) -> None:
        self.pack_name = pack_name
        super().__init__(f"Icon pack not found or not installed: '{pack_name}'")


class YAMLParseError(RedspecError):
    """Raised when the input YAML is invalid."""


class IncludeFileNotFoundError(RedspecError):
    """Raised when an included YAML file cannot be found."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Included file not found: '{path}'")


class UndefinedVariableError(RedspecError):
    """Raised when a ${variable} reference cannot be resolved."""

    def __init__(self, variable: str) -> None:
        self.variable = variable
        super().__init__(f"Undefined variable: '${{{variable}}}'")
