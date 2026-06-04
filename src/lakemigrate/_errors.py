class LakeMigrateError(Exception):
    pass


class ChecksumMismatchError(LakeMigrateError):
    pass


class DuplicateVersionError(LakeMigrateError):
    pass


class InvalidFilenameError(LakeMigrateError):
    pass
