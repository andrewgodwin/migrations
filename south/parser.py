import functools
from .actions import CreateModel, AlterModel


def no_context(func):
    "Decorator which should wrap handlers which should be outside a context"
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self.context is not None:
            raise self.syntax_error(
                "Keyword '%s' is not allowed here." % self.keyword_human,
            )
        return func(self, *args, **kwargs)
    return inner


def needs_context(func):
    "Decorator which should wrap handlers which should be outside a context"
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self.context is None:
            raise self.syntax_error(
                "Keyword '%s' is not allowed here." % self.keyword_human,
            )
        return func(self, *args, **kwargs)
    return inner


class MigrationParser(object):
    """
    Simplistic parser for the migration file format.
    There is no separate lexer as tokenising is done in here
    during the parse by newlines and whitespace.
    """

    def __init__(self, app_label, path):
        self.app_label = app_label
        self.path = path

    def syntax_error(self, message, klass=None):
        "Shortcut to make a well-created SyntaxError (or subclass)"
        klass = klass or SyntaxError
        error = klass(message)
        error.filename = self.path
        error.lineno = self.line_number
        return error

    def parse(self):
        "Runs the parse"
        # Set up parsing state
        self.context = None
        self.last_indent_level = 0
        self.actions = []
        # Go through the file line-by-line
        with open(self.path) as fh:
            for i, line in enumerate(fh):
                # Convert any tabs to 8 spaces, and warn
                line = line.replace("\t", " " * 8)
                # Detect the amount of indentation, then grab keywords
                self.indent_level = len(line) - len(line.lstrip(" "))
                self.keywords = line.split()
                self.line_number = i + 1
                # If the keyword is "create" or "delete", combine with the
                # next token to form a single new keyword
                if self.keywords[0] in ["create", "delete", "alter"]:
                    if len(self.keywords) == 1:
                        raise self.syntax_error("Expected second keyword after '%s'" % self.keywords[0])
                    elif self.keywords[1] in ["model", "field", "unique"]:
                        self.keyword_human = " ".join(self.keywords[:2])
                        self.keywords = ["_".join(self.keywords[:2])] + self.keywords[2:]
                    else:
                        raise self.syntax_error("Unexpected keyword combination '%s %s'" % tuple(self.keywords[:2]))
                else:
                    self.keyword_human = self.keywords[0]
                # If there's no indentation, reset the context
                if self.indent_level == 0:
                    if self.context is not None:
                        self.context.final_check()
                        if self.context.context_only:
                            self.actions = self.actions[:-1] + self.context.actions
                    self.context = None
                # If there's indentation without context, error
                elif self.context is None:
                    raise self.syntax_error(
                        "Unexpected indent (no preceding context)",
                        IndentationError,
                    )
                # Dispatch to the correct handling method
                handler = getattr(self, "handle_%s" % self.keywords[0], None)
                if handler is None:
                    raise self.syntax_error(
                        "Unknown keyword '%s'" % self.keyword_human,
                    )
                else:
                    handler()
            # Do sanity check, expand last context if needed
            if self.context is not None:
                self.context.final_check()
                if self.context.context_only:
                    self.actions = self.actions[:-1] + self.context.actions

    # Action shortcuts

    def name_action(self, method_name, error):
        """
        Shortcut for lines which have a name only
        and then call a method on the context, with an error if that
        fails.
        """
        if len(self.keywords) > 2:
            raise self.syntax_error("Too many arguments - expecting name only")
        name = self.keywords[1]
        try:
            getattr(self.context, method_name)(name)
        except AttributeError:
            raise self.syntax_error(error)

    def name_definition_action(self, method_name, error):
        """
        Shortcut for lines which have a name and definition
        and then call a method on the context, with an error if that
        fails.
        """
        name = self.keywords[1]
        definition = " ".join(self.keywords[2:])
        try:
            getattr(self.context, method_name)(name, definition)
        except AttributeError:
            raise self.syntax_error(error)

    @no_context
    def handle_create_model(self):
        "Starts off a model creation context"
        # Make sure there's no junk at the end of the line
        if len(self.keywords) > 2:
            raise self.syntax_error("Unexpected content after model name")
        # Work out if it's ModelName or appname.ModelName
        name = self.keywords[1]
        if "." in name:
            app_label, name = name.split(".", 1)
        else:
            app_label = self.app_label
        # Create the action and assign as context
        action = CreateModel(app_label, name)
        self.actions.append(action)
        self.context = action

    @no_context
    def handle_alter_model(self):
        "Starts off a model altering context"
        # Make sure there's no junk at the end of the line
        if len(self.keywords) > 2:
            raise self.syntax_error("Unexpected content after model name")
        # Work out if it's ModelName or appname.ModelName
        name = self.keywords[1]
        if "." in name:
            app_label, name = name.split(".", 1)
        else:
            app_label = self.app_label
        # Create the action and assign as context
        action = AlterModel(app_label, name)
        self.actions.append(action)
        self.context = action

    @needs_context
    def handle_field(self):
        "The 'field' keyword (for declaring fields inside create model)"
        self.name_definition_action("set_field", "A 'field' keyword is only allowed inside 'create model'.")

    @needs_context
    def handle_option(self):
        "'option' is allowed inside create or alter model."
        self.name_definition_action("set_option", "An 'option' keyword is only allowed inside 'create model' or 'alter model'.")

    @needs_context
    def handle_create_field(self):
        "'create field' is allowed inside alter model only."
        self.name_definition_action("create_field", "A 'create field' keyword is only allowed inside 'alter model'.")

    @needs_context
    def handle_delete_field(self):
        "'delete field' is allowed inside alter model only."
        self.name_action("delete_field", "A 'delete field' keyword is only allowed inside 'alter model'.")
