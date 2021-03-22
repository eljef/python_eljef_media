# -*- coding: UTF-8 -*-
# Copyright (c) 2021, Jef Oliver
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU Lesser General Public License,
# version 2.1, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# Authors:
# Jef Oliver <jef@eljef.me>
#
# __mp3_fix_args__.py : ElJef Fix MP3 CLI Program Args
"""ElJef Fix MP3 CLI Program Args"""

from eljef.core import cli

CMD_LINE_ARGS = [
    cli.Arg(['-v', '--version'], {'dest': 'version_out', 'action': 'store_true', 'help': 'Print version and exit.'}),
    cli.Arg(['--debug'], {'dest': 'debug_log', 'action': 'store_true', 'help': 'Enable debug output.'}),
    cli.Arg(['-c', '--correct-tags-only'], {'dest': 'tags_only', 'action': 'store_true',
                                            'help': 'Only correct tags on files.'}),
    cli.Arg(['-d', '--directory'], {'dest': 'mp3_directory', 'metavar': 'Artist', 'required': True,
                                    'help': 'Path to artist directory containing MP3 files.'}),
    cli.Arg(['-i', '--ignore-folder'], {'dest': 'ignore_folder', 'action': 'store_true',
                                        'help': 'Ignore existence of folder.jpg'}),
    cli.Arg(['-l', '--log-file'], {'dest': 'log_file', 'metavar': 'file.log',
                                   'help': 'Log file to use for storing logging statements.'}),
    cli.Arg(['-m', '--max-image-height'], {'dest': 'max_image_height', 'default': 600, 'type': int, 'metavar': '600',
                                           'help': 'The max height of images in pixels.'}),
    cli.Arg(['-t', '--target-volume'], {'dest': 'target_volume', 'default': 89.0, 'type': float, 'metavar': '89.0',
                                        'help': 'The target volume to feed to mp3gain.'})
]
