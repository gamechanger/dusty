import textwrap
from collections import defaultdict

class Warnings(object):
    def __init__(self):
        self._stored = defaultdict(list)

    @property
    def has_warnings(self):
        for namespace, warnings in self._stored.iteritems():
            if len(warnings) > 0:
                return True
        return False

    def clear_namespace(self, namespace):
        self._stored[namespace] = []

    def warn(self, namespace, message):
        self._stored[namespace].append(message)

    def pretty(self):
        result = ''
        for namespace in sorted(self._stored.keys()):
            result += ''.join(['WARNING ({}): {}\n'.format(namespace, '\n'.join(textwrap.wrap(message, 80)))
                               for message in self._stored[namespace]])
        return result

daemon_warnings = Warnings()
