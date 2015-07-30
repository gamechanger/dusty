import os

import dusty.constants
dusty.constants.BINARY = True

dusty.constants.PRERELEASE = os.getenv('PRERELEASE') == 'true'
