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
# __mp3_tag_dump_main__.py : ElJef Dump MP3 Tags CLI Program Main Functionality
"""ElJef Dump MP3 Tags CLI Program Main Functionality"""

import logging

import mutagen

from eljef.core import cli
from eljef.media.__version__ import VERSION
from eljef.media.cli.__mp3_dump_tags_args__ import CMD_LINE_ARGS
from eljef.media.cli.__mp3_dump_tags_vars__ import (DESCRIPTION, NAME)
from eljef.media.lib import mp3

LOGGER = logging.getLogger()


def cli_main() -> None:
    """Main functionality when run from CLI."""
    args = cli.args_simple(NAME, DESCRIPTION, CMD_LINE_ARGS)

    if args.version_out:
        cli.print_version(NAME, VERSION)

    mp3_data = mutagen.File(args.mp3_file)
    tags = mp3_data.tags.keys()

    print(f"{args.mp3_file}: ID3 Info")
    for tag in sorted(tags):
        if tag.startswith(mp3.FID_LYRICS) or tag == mp3.FID_APIC:
            continue

        print(f" * {tag} = {mp3_data.tags[tag]}")


if __name__ == '__main__':
    cli_main()
