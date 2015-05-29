import textwrap

class Warnings(object):
    def __init__(self):
        self._stored = []

    @property
    def has_warnings(self):
        return len(self._stored) != 0

    def warn(self, message):
        self._stored.append(message)

    def pretty(self):
        return '\n'.join(['WARNING: {}'.format('\n'.join(textwrap.wrap(message, 80)))
                          for message in self._stored])

daemon_warnings = Warnings()
