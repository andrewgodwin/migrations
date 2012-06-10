class ParsingError(SyntaxError):
    "Class for migration parsing errors"
    pass

class IndentationError(ParsingError):
    "Specific subclass for indentation errors"
    pass

class CircularDependency(StandardError):
    "Represents a circular dependency in migrations"
    pass
