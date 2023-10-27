# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Beet FLAC CLI Program Args"""

from eljef.core import cli

CMD_LINE_ARGS = [
    cli.Arg(['-v', '--version'], {'dest': 'version_out', 'action': 'store_true', 'help': 'Print version and exit.'}),
    cli.Arg(['--debug'], {'dest': 'debug_log', 'action': 'store_true', 'help': 'Enable debug output.'}),
    cli.Arg(['-b', '--beets-config'], {'dest': 'beets_config', 'metavar': 'path/to/beets/config.yaml',
                                       'help': 'Path to beets configuration file (if not in ${HOME}/.config/beets)'}),
    cli.Arg(['-d', '--directory'], {'dest': 'flac_directory', 'metavar': 'Artist', 'required': True,
                                    'help': 'Path to artist directory containing FLAC files.'}),
    cli.Arg(['-i', '--ignore-folder'], {'dest': 'ignore_folder', 'action': 'store_true',
                                        'help': 'Ignore existence of folder.jpg'}),
    cli.Arg(['-l', '--log-file'], {'dest': 'log_file', 'metavar': 'file.log',
                                   'help': 'Log file to use for storing logging statements.'}),
    cli.Arg(['-m', '--max-image-height'], {'dest': 'max_image_height', 'default': 600, 'type': int, 'metavar': '600',
                                           'help': 'The max height of images in pixels.'})
]
