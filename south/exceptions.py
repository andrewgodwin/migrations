class ParsingError(SyntaxError):
    "Class for migration parsing errors"
    pass

class IndentationError(ParsingError):
    "Specific subclass for indentation errors"
    pass
