class Configuration(dict):
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)

    def __eq__(self, subject):
        return self.__dict__ == subject

    def save(self):
        raise NotImplementedError('save is not yet implemented')
