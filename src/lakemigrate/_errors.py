class LakeMigrateError(Exception):
    """Base class for all lakemigrate exceptions."""


class ChecksumMismatchError(LakeMigrateError):
    """Raised when a migration file's checksum differs from the recorded value.

    Indicates that a previously applied migration file has been modified.
    lakemigrate treats this as an error to protect data integrity.
    """


class DuplicateVersionError(LakeMigrateError):
    """Raised when two migration files share the same version number."""


class InvalidFilenameError(LakeMigrateError):
    """Raised when a migration file does not follow the NNN__description.sql naming convention."""
