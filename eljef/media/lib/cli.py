# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Common ElJef Media CLI Functionality"""

import logging
import os
import shutil

from eljef.core import fops

LOGGER = logging.getLogger()

ALBUM_NFO = 'album.nfo'
"""ALBUM_NFO: name of the album nfo file"""


def album_dir_finish(nfo_file: str, nfo_data: dict) -> None:
    """Copies cover.jpg to folder.jpg, and saves album.nfo

    Args:
        nfo_file: path to nfo file to write
        nfo_data: dictionary of NFO data to save to album.nfo
    """
    LOGGER.info("   ** cover.jpg -> folder.jpg")
    shutil.copyfile("cover.jpg", 'folder.jpg')

    LOGGER.info("   ** album.nfo")
    fops.file_write_convert(nfo_file, fops.XML, nfo_data)


def exit_with_error(error_str: str) -> None:
    """Exits a program with the specified error string

    Args:
        error_str: Error string to print before exiting.

    Raises:
        SystemExit: Always
    """
    LOGGER.error(error_str)
    raise SystemExit(1)


def check_media_dir(path: str) -> str:
    """Checks if the specified directory exists.

    Args:
        path: path to check

    Returns:
        A normalized path to use for processing
    """
    if not os.path.exists(path):
        exit_with_error(f"Specified directory does not exist: {path}")

    dir_to_process = os.path.abspath(path)
    if os.path.islink(dir_to_process):
        dir_to_process = os.readlink(dir_to_process)

    if not os.path.isdir(dir_to_process):
        exit_with_error(f"Specified directory path is not a directory or link to a directory: {path}")

    return dir_to_process


def get_media_dirs(path: str, media_type: str, error_msg: str) -> set:
    """Returns a list of directories containing files of the specified type, exiting the CLI program if none exist.

    Args:
        path: base directory to search for media files in
        media_type: type of media to look for (file extension)
        error_msg: the error message to exit with if no media files are found

    Returns:
        A set containing folders that contain media files.
    """
    media_dirs = fops.list_dirs_by_extension(path, media_type)
    if len(media_dirs) < 1:
        exit_with_error(error_msg)

    return media_dirs
