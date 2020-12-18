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
# comic.py : ElJef Comic Archive Manipulation
"""ElJef Comic Archive Manipulation

ElJef Comic Archive Manipulation.
"""

from collections import (namedtuple, OrderedDict)
from pathlib import Path

import logging
import os
import shutil
import subprocess
import zipfile

from PIL import Image

from eljef.core import fops

LOGGER = logging.getLogger(__name__)

COMIC_INFO_XML = 'ComicInfo.xml'
"""Name of the Metadata XML file for a comic book."""

Images = namedtuple('Images', 'jpg png webp types')
"""Images holds relative paths to image files found in a comic archive

Attributes:
    jpegs (list): List of JPEG images found in archive
    pngs (list): List of PNG images found in archive
    webp (list): List of WEBP images found in archive
    types (int): Number of types of images found in archive
"""

_DEFAULT_IMAGE_TYPE = 'jpg'
_SUPPORTED_IMAGE_TYPES = {'jpg', 'png', 'web'}


def compress(comic_book: str, extracted_path: str, file_list: list) -> None:
    """Compresses images into a new comic book file.

    Args:
        comic_book: Full path to the comic book file to create.
        extracted_path: Path to folder containing files to compress.
        file_list: List of files to add to the comic book.
    """
    with fops.pushd(extracted_path):
        with zipfile.ZipFile(comic_book, 'w', compression=zipfile.ZIP_STORED) as zip_file:
            for file in sorted(file_list):
                zip_file.write(file)


def copy_images(orig_path: str, new_path: str, images: list, convert_to: str) -> list:
    """Copies comic book page images to new location, converting if requested.

    Args:
        orig_path: Path to folder holding the extracted original comic book.
        new_path: Path to the folder that will hold the new comic book.
        images: List of image paths relative to ```orig_path``` to be copied.
        convert_to: If set, convert image files to the specified type.

    Returns:
        A list of image files to be compress into the new comic book archive
    """
    new_ext = convert_to if convert_to else _DEFAULT_IMAGE_TYPE
    if new_ext not in _SUPPORTED_IMAGE_TYPES:
        raise ValueError(f"convert_to = {convert_to}, must be one of: {', '.join(_SUPPORTED_IMAGE_TYPES)}")

    current_page = 0
    new_images = []

    for file in sorted(images):
        new_file = f"P{current_page:05d}.{new_ext}"
        LOGGER.debug("%s -> %s", file, new_file)
        if not convert_to:
            shutil.copyfile(os.path.join(orig_path, file), os.path.join(new_path, new_file))
        else:
            image_file = Image.open(fr'{os.path.join(orig_path, file)}')
            image_file.save(fr'{os.path.join(new_path, new_file)}')

        new_images.append(new_file)
        current_page += 1

    return new_images


def copy_info(orig_info: str, new_info: str, no_info: str, new_base: str, pages: list) -> list:
    """Copies the ComicInfo.xml file over, fixing pages entries.

    Args:
        orig_info: Full path to the original ComicInfo.xml.
        new_info: Full path to the new ComicInfo.xml.
        no_info: Full path to NoComicInfo file if no ComicInfo.xml is found.
        new_base: Full path to the directory containing comic book files.
        pages: List of pages for the new comic book.
    """
    if not os.path.isfile(orig_info):
        Path(no_info).touch()
        return pages

    comic_info_data = fops.file_read_convert(orig_info, fops.XML, default=True)
    if comic_info_data.get('ComicInfo'):
        comic_info_pages_page = []
        page_count = 0
        for page in sorted(pages):
            path = os.path.join(new_base, page)
            image = Image.open(fr'{path}')
            page_info = OrderedDict()
            page_info['@Image'] = str(page_count)
            page_info['@ImageWidth'] = str(image.width)
            page_info['@ImageHeight'] = str(image.height)
            image.close()
            comic_info_pages_page.append(page_info)
            page_count += 1

        comic_info_pages_page[0]['@Type'] = 'FrontCover'
        comic_info_data['ComicInfo']['Pages'] = OrderedDict()
        comic_info_data['ComicInfo']['Pages']['Page'] = comic_info_pages_page

    fops.file_write_convert(new_info, fops.XML, comic_info_data)

    return pages + [COMIC_INFO_XML]


def extract(comic: str, path: str, debug: bool = False) -> None:
    """Extracts a comic file to the specified directory.

    Args:
        comic: Full path to comic file.
        path: Full path to directory to extract comic file to.
        debug: Enable output of decompression program information.
    """
    with fops.pushd(path):
        try:
            subprocess.run(["unar", "-D", comic], capture_output=not debug, check=True)
        except subprocess.CalledProcessError as error:
            if error.stderr:
                LOGGER.error(error.stderr)
            elif error.stdout:
                LOGGER.error(error.stdout)
            raise


def filter_pages(files: list) -> list:
    """Filters names of files to determine if they are they are numbered pages.

    Args:
        files: A list of file names to filter.

    Returns:
        A list of filtered file names.

    Note:
        This filters based on the assumption that a file has a page number at end of the name.
        ie: comic_page_01.jpg
    """
    filtered_files = []

    for file in files:
        name, _ = file.rsplit('.', 1)
        if name[-1].isdigit():
            filtered_files.append(file)
        else:
            LOGGER.warning("removing file  %s", file)

    return filtered_files


def get_images(path: str, filter_images: bool) -> Images:
    """Builds a list of images found in a comic archive.

    Args:
        path: Full path to folder containing an uncompressed comic archive.
        filter_images: Filter out images that are not flagged as a valid page.

    Returns:
        An Images tuple with image information.
    """
    jpeg = fops.list_files_by_extension(path, 'jpg')
    jpeg += fops.list_files_by_extension(path, 'JPG')
    jpeg += fops.list_files_by_extension(path, 'jpeg')
    jpeg += fops.list_files_by_extension(path, 'JPEG')
    png = fops.list_files_by_extension(path, 'png')
    png += fops.list_files_by_extension(path, 'PNG')
    webp = fops.list_files_by_extension(path, 'webp')
    webp += fops.list_files_by_extension(path, 'WEBP')
    types = 0

    if len(jpeg) > 0:
        types += 1
    if len(png) > 0:
        types += 1
    if len(webp) > 0:
        types += 1

    if filter_images:
        jpeg = filter_pages(jpeg)
        png = filter_pages(png)
        webp = filter_pages(webp)

    return Images(jpeg, png, webp, types)
