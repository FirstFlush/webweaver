


class ProjectHandler:
    _instance = None
    pipeline_class = None
    validation_class = None

    @classmethod
    def initialize_project(cls):
        return None

    @classmethod
    def finish(cls):
        cls._instance = None