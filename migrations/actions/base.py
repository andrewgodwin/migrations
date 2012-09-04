class Action(object):
    "Base class for actions"

    def alter_state(self, project_state):
        "Mutates the project_state with the changes this Action represents"
        raise NotImplementedError()

    def alter_database(self, from_state, to_state, database, forwards):
        "Run to alter the database. Should call Django's alteration backends directly."
        raise NotImplementedError()
