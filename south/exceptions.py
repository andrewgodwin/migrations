class ParsingError(SyntaxError):
    "Class for migration parsing errors"
    pass


class IndentationError(ParsingError):
    "Specific subclass for indentation errors"
    pass


class MigrationError(StandardError):
    "General class for migration errors"
    pass


class InvalidDependency(MigrationError):
    "Represents a dependency that does not exist"
    pass


class NonexistentDependency(MigrationError):
    "Represents a dependency that does not exist"
    pass


class CircularDependency(MigrationError):
    "Represents a circular dependency in migrations"
    pass


class NonexistentMigration(MigrationError):
    "Raised when a migration file cannot be found"
    pass
