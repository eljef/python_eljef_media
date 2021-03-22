# -*- coding: UTF-8 -*-
# Copyright (c) 2020, Jef Oliver
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
# __comic_fix_args__.py : ElJef Fix Comic CLI Program Args
"""ElJef Fix Comic CLI Program Args"""

from eljef.core import cli

CMD_LINE_ARGS = [
    cli.Arg(['-v', '--version'], {'dest': 'version_out', 'action': 'store_true', 'help': 'Print version and exit.'}),
    cli.Arg(['-d', '--debug'], {'dest': 'debug_log', 'action': 'store_true', 'help': 'Enable debug output.'}),
    cli.Arg(['-f', '--file'], {'dest': 'comic_file', 'metavar': 'comic.cbz', 'help': 'Path to comic book file.',
                               'required': True}),
    cli.Arg(['--convert-images'], {'dest': 'images_format', 'metavar': 'format',
                                   'help': 'Convert all images in comic book to specified format.',
                                   'choices': {'jpg', 'png', 'webp'}}),
    cli.Arg(['--copy-only'], {'dest': 'copy_only', 'metavar': 'format',
                              'help': 'Copy only images of the specified format, discarding all others.',
                              'choices': {'jpg', 'png', 'webp'}}),
    cli.Arg(['--allow-multiple-image-formats'], {'dest': 'allow_image_multi', 'action': 'store_true',
                                                 'help': 'Allow multiple image formats in comic book.'}),
    cli.Arg(['--filter-pages'], {'dest': 'filter_pages', 'action': 'store_true',
                                 'help': 'Filter image files that do not contain a page number out.'})
]
