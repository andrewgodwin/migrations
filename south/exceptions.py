class ParsingError(SyntaxError):
    "Class for migration parsing errors"
    pass


class IndentationError(ParsingError):
    "Specific subclass for indentation errors"
    pass


class DependencyError(StandardError):
    "General class for dependency errors"
    pass


class InvalidDependency(DependencyError):
    "Represents a dependency that does not exist"
    pass


class NonexistentDependency(DependencyError):
    "Represents a dependency that does not exist"
    pass


class CircularDependency(DependencyError):
    "Represents a circular dependency in migrations"
    pass
