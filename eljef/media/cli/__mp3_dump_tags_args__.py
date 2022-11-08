# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Dump MP3 Tags CLI Program Args"""

from eljef.core import cli

CMD_LINE_ARGS = [
    cli.Arg(['-v', '--version'], {'dest': 'version_out', 'action': 'store_true', 'help': 'Print version and exit.'}),
    cli.Arg(['-f', '--file'], {'dest': 'mp3_file', 'metavar': 'MP3', 'required': True,
                               'help': 'File to dump ID3 tags from.'})
]
