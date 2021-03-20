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
# image.py : ElJef Image File Manipulation
"""ElJef Image File Manipulation."""

import logging
import os

from typing import Tuple
from PIL import Image

from eljef.core import fops

LOGGER = logging.getLogger(__name__)


def _calc_size(max_height: int, cur_width: int, cur_height: int) -> Tuple[int, int]:
    """Calculates the new size of an image based upon max_height.

    Args:
        max_height: New height for image
        cur_width: Current width of image
        cur_height: Current height of image

    Returns:
        A tuple with the new width and height
    """
    new_height_percent = (max_height / float(cur_height))
    new_width = int((float(cur_width) * float(new_height_percent)))

    return new_width, max_height


def _convert_and_resize(path: str, mid: str, target: str, max_height: int, encoding: str) -> None:
    """Converts and resizes an image.

    Args:
        path: Path to original file
        mid: Path to mid step file.
        target: Path to new file.
        max_height: New height for image.
        encoding: Image encoding. (ie. RGB, RGBA)
    """
    LOGGER.debug("Converting '%s' to '%s'", path, mid)
    with Image.open(fr'{path}') as image_file:
        new_width, new_height = _calc_size(max_height, image_file.size[0], image_file.size[1])
        with image_file.resize((new_width, new_height), Image.ANTIALIAS) as resized_image:
            with resized_image.convert(encoding) as new_image:
                new_image.save(fr'{mid}')
                new_image.close()

    fops.delete(target)
    LOGGER.debug("%s -> %s", mid, target)
    os.rename(fr'{mid}', fr'{target}')


def cover_fix(path: str, max_height: int) -> None:
    """Converts and resizes cover.ext

    Converts cover.ext to cover.jpg and resizes it to `max_height`, maintaining
    aspect ratio.

    Args:
        path: Path to cover.ext
        max_height: The max height the image is allowed to be.

    Raises:
        ValueError: If the provided path is not a cover
    """
    orig, _ = os.path.splitext(path)
    if orig[-5:] != 'cover':
        raise ValueError('Provided path is not a cover?')

    target = f"{orig}.jpg"
    mid = f"{orig}.new.jpg"

    _convert_and_resize(path, mid, target, max_height, 'RGB')


def discart_fix(path: str, max_height: int) -> None:
    """Converts and resizes discart

    Converts discart.ext to discart.png and resizes it to `max_height`,
    maintaining aspect ratio.

    Args:
        path: Path to discart.ext
        max_height: The max height the image is allowed to be.

    Raises:
        ValueError: If the provided path is not a discart.
    """
    orig, _ = os.path.splitext(path)
    if orig[-7:] != 'discart':
        raise ValueError('Provided path is not a discart?')

    target = f"{orig}.png"
    mid = f"{orig}.new.png"

    _convert_and_resize(path, mid, target, max_height, 'RGBA')


def image_find(path: str, image_name: str) -> str:
    """Checks if a image.ext exists in `path`

    Args:
        path: Directory to check for image.ext in.
        image_name: Name of image to look for without extension.

    Returns:
        Name of image.ext file if one is found, blank otherwise.
    """
    LOGGER.debug("Searching for %s.ext in: %s", image_name, path)
    with fops.pushd(path):
        for image_ext in ('jpg', 'png', 'webp', 'gif'):
            image_file = f'{image_name}.{image_ext}'
            if os.path.isfile(image_file):
                return image_file

    return ''
