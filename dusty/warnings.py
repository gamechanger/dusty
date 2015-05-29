import textwrap

class Warnings(object):
    def __init__(self):
        self.stored = []

    @property
    def has_warnings(self):
        return self.stored != []

    def warn(self, message):
        self.stored.append(message)

    def pretty(self):
        return '\n'.join(['WARNING: {}'.format('\n'.join(textwrap.wrap(message, 80)))
                          for message in self.stored])

daemon_warnings = Warnings()
