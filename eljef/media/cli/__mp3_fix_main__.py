# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Fix MP3 CLI Program Main Functionality"""

import logging
import os

from eljef.core import (applog, cli, fops)
from eljef.media.__version__ import VERSION
from eljef.media.cli.__mp3_fix_args__ import CMD_LINE_ARGS
from eljef.media.cli.__mp3_fix_vars__ import (DESCRIPTION, NAME)
from eljef.media.lib import (mp3, image)
from eljef.media.lib.cli import (ALBUM_NFO, album_dir_finish, check_media_dir, exit_with_error, get_media_dirs)

# noinspection PyPackageRequirements
# pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa


LOGGER = logging.getLogger()

__REQUIRED_EXECS = ['mp3gain']


def _main_process_mp3_dir_mp3s_tags_only(mp3_list: list) -> None:
    """Process only the tags on individual MP3s

    Args:
        mp3_list: List of MP3 files to process
    """
    LOGGER.info("   ** Correcting tags")
    for mp3_file in mp3_list:
        mp3.remove_ape_tags(mp3_file)
        mp3.correct_replaygain_tags(mp3_file)


def _main_process_mp3_dir_mp3s(mp3_list: list, cover_image: str, target_volume: float, debug: bool) -> None:
    """Process individual MP3s

    Args:
        mp3_list: List of MP3 files to process
        cover_image: Name of the image to use for the front cover.
        target_volume: Volume, in decibels, mp3gain should adjust a track to.
        debug: Enable debug logging when True
    """
    LOGGER.info("   ** Removing previous replaygain tags and APE tags")
    for mp3_file in mp3_list:
        mp3.remove_ape_tags(mp3_file)
        mp3.remove_replaygain_tags(mp3_file)

    LOGGER.info("   ** Leveling gain with mp3gain")
    mp3.mp3gain(mp3_list, target_volume, debug)

    LOGGER.info("   ** Calculating replaygain and adding tags")
    mp3.replaygain(mp3_list, target_volume)

    LOGGER.info("   ** Correcting tags and images")
    for mp3_file in mp3_list:
        mp3.remove_ape_tags(mp3_file)
        mp3.fix_cover_tag(mp3_file, cover_image)
        mp3.correct_replaygain_tags(mp3_file)


def _main_process_mp3_dir(base: str, path: str, image_height: int, target_volume: float, **kwargs) -> None:
    """Main MP3 directory processing function.

    Args:
        base: Base path holding directories of MP3s (Artist Directory)
        path: Sub-directory holding MP3s (Album Directory)
        image_height: The height that cover.jpg should be resized to.
        target_volume: Volume, in decibels, mp3gain should adjust a track to.

    Keyword Args:
        debug (bool): Enable debug logging when True
        ignore_folder (bool): Ignore the presence of folder.jpg
        tags_only (bool): Only correct tags on MP3 files
    """
    full_path = os.path.join(base, path)
    LOGGER.debug("Processing: %s", full_path)

    mp3_list = fops.list_files_by_extension(full_path, 'mp3')
    nfo_data = mp3.album_nfo_from_mp3_file(os.path.join(full_path, mp3_list[0]))

    LOGGER.info(" * %s", nfo_data.get('album').get('title'))

    if kwargs.get('tags_only'):
        with fops.pushd(full_path):
            _main_process_mp3_dir_mp3s_tags_only(mp3_list)
            return

    folder_image = image.image_find(full_path, 'folder')

    if folder_image and not kwargs.get('ignore_folder', False):
        LOGGER.warning("   ** %s found: Skipping because already processed", folder_image)
        return

    cover_image = image.image_find(full_path, 'cover')
    discart_image = image.image_find(full_path, 'discart')

    if not cover_image:
        LOGGER.error("   ** No cover image found: Skipping.")
        return

    with fops.pushd(full_path):
        cover_image, discart_image = image.process_dir_images(cover_image, folder_image, discart_image, image_height)
        _main_process_mp3_dir_mp3s(mp3_list, cover_image, target_volume, kwargs.get('debug'))
        album_dir_finish(ALBUM_NFO, nfo_data)


def main(**kwargs) -> None:
    """Main Fix MP3 functionality.

    Keyword Args:
        debug (bool): If True, enables debug logging.
        directory (str): Path to directory to process.
        ignore_folder (bool): Ignore the existence of folder.jpg
        image_height (int): Max image height for resized images.
        tags_only (bool): Only correct the tags on MP3 files.
        target_volume (float): Target volume for mp3 files via mp3gain.
    """
    _ = Gst.init(None)

    directory = kwargs.get('directory')
    mp3dirs = get_media_dirs(directory, 'mp3', 'No MP3 files found')

    for dir_to_process in sorted(mp3dirs):
        _main_process_mp3_dir(directory, dir_to_process, kwargs.get('image_height'), kwargs.get('target_volume'),
                              debug=kwargs.get('debug'), ignore_folder=kwargs.get('ignore_folder'),
                              tags_only=kwargs.get('tags_only'))


def cli_main() -> None:
    """Main functionality when run from CLI."""
    args = cli.args_simple(NAME, DESCRIPTION, CMD_LINE_ARGS)

    if args.version_out:
        cli.print_version(NAME, VERSION)

    applog.setup_app_logging(args.debug_log, args.log_file)

    if args.max_image_height < 1:
        exit_with_error(f"Max image height must be greater than 0. Specified {args.max_image_height}")
    if args.target_volume < float(1):
        exit_with_error(f"Target volume must be greater than 0. Specified {args.target_volume}")

    dir_to_process = check_media_dir(args.mp3_directory)

    fops.required_executables(__REQUIRED_EXECS)

    LOGGER.info("Processing: %s", args.mp3_directory)
    main(debug=args.debug_log, directory=dir_to_process, ignore_folder=args.ignore_folder,
         image_height=args.max_image_height, tags_only=args.tags_only, target_volume=args.target_volume)


if __name__ == '__main__':
    cli_main()
