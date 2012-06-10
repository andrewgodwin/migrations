class Action(object):
    "Base class for actions"

    # If this is True, the action only exists temporarily for parsing
    # and is replaced by self.actions once parsing is complete.
    context_only = False

    def final_check(self):
        "Entrypoint for a final sanity check for context-type actions"
        pass

    def alter_state(self, project_state):
        "Mutates the project_state with the changes this Action represents"
        raise NotImplementedError()

    def alter_database(self, from_state, to_state, database, forwards):
        "Run to alter the database. Should call Django's alteration backends directly."
        raise NotImplementedError()
