'''
ESSA Connect :: Electronic Grade Book Assistant Connector
Copyright (C) 2025 Mariusz Duka
This file is part of ESSA and is licensed under the GNU GPLv3 or later.
See the LICENSE file for full text.
'''

import os
import configparser
from .version import VERSION

essa_config = configparser.ConfigParser()
essa_config.read(os.path.dirname(__file__) + '/essa.conf', encoding='utf8')

GITHUB = 'https://github.com/mariuszduka/essa'
HOMEPAGE = 'https://github.com/mariuszduka/essa'