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
# __mp3_dump_tags_args__.py : ElJef Dump MP3 Tags CLI Program Args
"""ElJef Dump MP3 Tags CLI Program Args"""

from eljef.core import cli

CMD_LINE_ARGS = [
    cli.Arg(['-v', '--version'], {'dest': 'version_out', 'action': 'store_true', 'help': 'Print version and exit.'}),
    cli.Arg(['-f', '--file'], {'dest': 'mp3_file', 'metavar': 'MP3', 'required': True,
                               'help': 'File to dump ID3 tags from.'})
]
