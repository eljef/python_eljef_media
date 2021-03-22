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
# __fix_comic_args__.py : ElJef Fix MP3 CLI Program Main Functionality
"""ElJef Fix MP3 CLI Program Main Functionality"""

import logging
import os
import shutil

from eljef.core import (applog, cli, fops)
from eljef.media.__version__ import VERSION
from eljef.media.cli.__fix_mp3_args__ import CMD_LINE_ARGS
from eljef.media.cli.__fix_mp3_vars__ import (DESCRIPTION, NAME)
from eljef.media.lib import (mp3, image)

# noinspection PyPackageRequirements
# pylint: disable=wrong-import-position,wrong-import-order
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa


LOGGER = logging.getLogger()

__ALBUM_NFO = 'album.nfo'
__REQUIRED_EXECS = ['mp3gain']


def _main_get_mp3_dirs(path: str) -> set:
    """Returns a list of directories containing mp3s, exiting the CLI program if none exist.

    Args:
        path: base directory to search for MP3s in.

    Returns:
        A set containing folders that contain MP3 files.
    """
    mp3dirs = fops.list_dirs_by_extension(path, 'mp3')
    if len(mp3dirs) < 1:
        LOGGER.error("No MP3 files found")
        raise SystemExit

    return mp3dirs


def _main_process_mp3_dir_finish(nfo_data: dict) -> None:
    """Copies cover.jpg to folder.jpg, and saves album.nfo

    Args:
        nfo_data: dictionary of NFO data to save to album.nfo
    """
    LOGGER.info(" ** cover.jpg -> folder.jpg")
    shutil.copyfile("cover.jpg", 'folder.jpg')

    LOGGER.info(" ** album.nfo")
    fops.file_write_convert(__ALBUM_NFO, fops.XML, nfo_data)


def _main_process_mp3_dir_images(cover_image: str, folder_image: str, discart_image: str, image_height: int) -> None:
    """Processes images in the MP3 directory (Album Directory)

    Args:
        cover_image: Name of cover image. (Typically cover.jpg)
        folder_image:  Name of folder image. (Typically folder.jpg)
        discart_image: Name of discart image. (Typically discart.png)
        image_height: The height that images should be resized to. (Maintaining aspect ratio.)
    """
    fops.delete(folder_image)

    image.cover_fix(cover_image, image_height)
    if cover_image != "cover.jpg":
        fops.delete(cover_image)

    if discart_image:
        image.discart_fix(discart_image, image_height)
        if discart_image != "discart.png":
            fops.delete(discart_image)


def _main_process_mp3_dir_mp3s_tags_only(mp3_list: list) -> None:
    """Process only the tags on individual MP3s

    Args:
        mp3_list: List of MP3 files to process
    """
    LOGGER.info(" ** Correcting tags")
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
    LOGGER.info(" ** Removing previous replaygain tags and APE tags")
    for mp3_file in mp3_list:
        mp3.remove_ape_tags(mp3_file)
        mp3.remove_replaygain_tags(mp3_file)

    LOGGER.info(" ** Calculating gain with mp3gain")
    mp3.mp3gain(mp3_list, target_volume, debug)

    LOGGER.info(" ** Calculating replaygain")
    mp3.replaygain(mp3_list, target_volume)

    LOGGER.info(" ** Correcting tags")
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
    debug = kwargs.get('debug', False)
    ignore_folder = kwargs.get('ignore_folder', False)

    full_path = os.path.join(base, path)
    LOGGER.debug("Processing: %s", full_path)

    mp3_list = fops.list_files_by_extension(full_path, 'mp3')
    nfo_data = mp3.album_nfo_from_file(os.path.join(full_path, mp3_list[0]))

    LOGGER.info("Processing: %s/%s", nfo_data.get('album').get('artistdesc'), nfo_data.get('album').get('title'))

    if kwargs.get('tags_only'):
        _main_process_mp3_dir_mp3s_tags_only(mp3_list)
        return

    folder_image = image.image_find(full_path, 'folder')

    if folder_image and not ignore_folder:
        LOGGER.warning(" ** %s found: Skipping because already processed", folder_image)
        return

    cover_image = image.image_find(full_path, 'cover')
    discart_image = image.image_find(full_path, 'discart')

    if not cover_image:
        LOGGER.error(" ** No cover image found: Skipping.")
        return

    with fops.pushd(full_path):
        _main_process_mp3_dir_images(cover_image, folder_image, discart_image, image_height)
        _main_process_mp3_dir_mp3s(mp3_list, cover_image, target_volume, debug)
        _main_process_mp3_dir_finish(nfo_data)


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
    debug = kwargs.get('debug')
    directory = kwargs.get('directory')
    ignore_folder = kwargs.get('ignore_folder')
    image_height = kwargs.get('image_height')
    target_volume = kwargs.get('target_volume')

    _ = Gst.init(None)

    mp3dirs = _main_get_mp3_dirs(directory)
    for dir_to_process in sorted(mp3dirs):
        _main_process_mp3_dir(directory, dir_to_process, image_height, target_volume,
                              debug=debug, ignore_folder=ignore_folder, tags_only=kwargs.get('tags_only'))


def cli_main() -> None:
    """Main functionality when run from CLI."""
    args = cli.args_simple(NAME, DESCRIPTION, CMD_LINE_ARGS)

    if args.version_out:
        cli.print_version(NAME, VERSION)

    applog.setup_app_logging(args.debug_log, args.log_file)

    if args.max_image_height < 1:
        raise ValueError("Max image height must be greater than 0. Specified %d" % args.max_image_height)
    if args.target_volume < float(1):
        raise ValueError("Target volume must be greater than 0. Specified %f" % args.target_volume)

    if not os.path.exists(args.mp3_directory):
        raise FileNotFoundError("Specified directory does not exist: %s" % args.mp3_directory)

    dir_to_process = os.path.abspath(args.mp3_directory)

    if not os.path.isdir(dir_to_process):
        raise NotADirectoryError("Specified directory path is not a directory: %s" % args.mp3_directory)

    fops.required_executables(__REQUIRED_EXECS)

    LOGGER.info("Processing: %s", args.mp3_directory)
    main(debug=args.debug_log, directory=dir_to_process, ignore_folder=args.ignore_folder,
         image_height=args.max_image_height, tags_only=args.tags_only, target_volume=args.target_volume)


if __name__ == '__main__':
    cli_main()
