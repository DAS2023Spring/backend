class ContextDefault:
    requires_context = True

    def __init__(self, field):
        self.field = field

    def __call__(self, serializer_field):
        return serializer_field.context[self.field]
