# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Fix Comic CLI Program Main Functionality"""
from collections import namedtuple

import logging
import os
import tempfile

from eljef.core import (applog, cli, fops)
from eljef.media.__version__ import VERSION
from eljef.media.cli.__comic_fix_args__ import CMD_LINE_ARGS
from eljef.media.cli.__comic_fix_vars__ import (DESCRIPTION, NAME)
from eljef.media.lib import comic

LOGGER = logging.getLogger()

_BookPaths = namedtuple('_BookPaths', 'file extracted info')
"""Paths for an individual book.

Attributes:
    file (str): Full path to the comic book file.
    extracted (str): Full path to the folder holding the extracted comic book.
    info (str): Full path to the comic book metadata file.
"""

_Paths = namedtuple('_Paths', 'base ext name no_info new orig temp')
"""Paths for a comic book project.

Attributes:
    base (str): Full path to the folder holding the comic book file.
    ext (str): Extension used by the original comic book.
    name (str): Name of the comic book file.
    no_info (str): Full path to the NoComicInfo file that is created if comic
                   metadata is missing.
    new (_BookPaths): Object containing information for the new comic book
                       file.
    orig (_BookPaths): Object containing information for the original comic
                        book file.
"""


def _clean_exit(paths: _Paths, exit_str: str = None) -> None:
    """Cleanup before exiting.

    Args:
        paths: Paths named tuple.
        exit_str: If provided, raises a SystemExit with the provided message.
    """
    fops.delete(paths.temp)
    if exit_str:
        LOGGER.error(exit_str)
        raise SystemExit(1)


def _create_temp(paths: _Paths) -> None:
    """Creates temporary directories needed for working with a comic book.

    Args:
        paths: _Paths object created by ```_get_paths()```
    """
    fops.delete(paths.temp)
    os.makedirs(paths.new.extracted)
    os.makedirs(paths.orig.extracted)


def _get_image_list(images: comic.Images, allow_multi: bool, copy_only: str) -> list:
    """Returns a list of images to be copied.

    Args:
        images: comic.Images object containing paths to images to be copied.
        allow_multi: Allow multiple image formats.
        copy_only: Copy only images of the specified format.
    """
    if allow_multi:
        return images.jpg + images.png + images.webp
    if copy_only:
        return getattr(images, copy_only)
    if len(images.webp) > 0:
        return images.webp
    if len(images.png) > 0:
        return images.png

    return images.jpg


def _get_paths(comic_file: str) -> _Paths:
    """Parse the path to the comic book file and the comic book name.

    Parses the path to the comic book file, the name and extension of the comic
    book, and builds paths that will be used in working with the comic book
    file.

    Args:
        comic_file: Full path to the comic book file.

    Returns:
        A filled _Paths namedtuple.
    """
    base = os.path.dirname(comic_file)
    name, ext = os.path.basename(comic_file).rsplit(".", 1)
    no_info = f"{comic_file}.NoComicInfo"

    temp = os.path.join(tempfile.gettempdir(), NAME, name)

    new_file = os.path.join(base, f"{name}.cbz")
    new_extracted = os.path.join(temp, "new")
    new_info = os.path.join(new_extracted, comic.COMIC_INFO_XML)

    orig_file = os.path.join(base, f"{name}.orig.{ext}")
    orig_extracted = os.path.join(temp, "orig")
    orig_info = os.path.join(orig_extracted, comic.COMIC_INFO_XML)

    return _Paths(base, ext, name, no_info, _BookPaths(new_file, new_extracted, new_info),
                  _BookPaths(orig_file, orig_extracted, orig_info), temp)


def main(**kwargs) -> None:
    """Main Fix Comic functionality

    Keyword Args:
        comic_file (str): Full path to comic book file.
        debug (bool): If True, enables debug output.
        copy_only (str): If set, copy only images of the specified type.
        img_conv (str): If set, convert images to specified type.
        img_filter (bool): If True, filters out images files that do not contain a page number.
        img_multi (bool): If True, allow multiple image formats in comic book file.
    """
    paths = _get_paths(kwargs.get('comic_file'))
    _create_temp(paths)
    comic.extract(kwargs.get('comic_file'), paths.orig.extracted, debug=kwargs.get('debug'))
    images = comic.get_images(paths.orig.extracted, filter_images=kwargs.get('img_filter'))

    if images.types == 0:
        _clean_exit(paths, "no image files found")
    if images.types > 1 and not kwargs.get('copy_only') and not kwargs.get('img_conv') and not kwargs.get('img_multi'):
        _clean_exit(paths, "multiple image formats found but not explicitly allowed and conversion not specified")

    images = _get_image_list(images, kwargs.get('img_multi'), kwargs.get('copy_only'))
    if kwargs.get('copy_only') and not images:
        _clean_exit(paths, f"only {kwargs.get('copy_only')} files were set to be copied, but none were found")

    to_compress = comic.copy_images(paths.orig.extracted, paths.new.extracted, images, kwargs.get('img_conv'))
    os.rename(kwargs.get('comic_file'), paths.orig.file)
    to_compress = comic.copy_info(paths.orig.info, paths.new.info, paths.no_info, paths.new.extracted, to_compress)
    comic.compress(paths.new.file, paths.new.extracted, to_compress)
    _clean_exit(paths)


def cli_main() -> None:
    """Main functionality when run from CLI."""
    args = cli.args_simple(NAME, DESCRIPTION, CMD_LINE_ARGS)

    if args.version_out:
        cli.print_version(NAME, VERSION)

    applog.setup_app_logging(args.debug_log)

    if not os.path.exists(args.comic_file):
        raise FileNotFoundError(f"'{args.comic_file}' not found")
    if not os.path.isfile(args.comic_file):
        raise IsADirectoryError(f"'{args.comic_file}' is not a file")

    comic_file = os.path.realpath(args.comic_file)
    LOGGER.info(" -- Processing %s", comic_file)

    main(comic_file=comic_file,
         copy_only=args.copy_only,
         debug=args.debug_log,
         img_conv=args.images_format,
         img_filter=args.filter_pages,
         img_multi=args.allow_image_multi)


if __name__ == '__main__':
    cli_main()
