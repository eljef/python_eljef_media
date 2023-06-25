# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Image File Manipulation"""

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
    new_height_percent = max_height / float(cur_height)
    new_width = int((float(cur_width) * float(new_height_percent)))

    return new_width, max_height


def _convert_and_resize(path: str, mid: str, target: str, max_height: int, encoding: str) -> str:
    """Converts and resizes an image.

    Args:
        path: Path to original file
        mid: Path to mid-step file.
        target: Path to new file.
        max_height: New height for image.
        encoding: Image encoding. (ie. RGB, RGBA)

    Returns:
        path to new file.
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

    return target


def cover_fix(path: str, max_height: int) -> str:
    """Converts and resizes cover.[ext]

    Converts cover.[ext] to cover.jpg and resizes it to `max_height`, maintaining
    aspect ratio.

    Args:
        path: Path to cover.[ext]
        max_height: The max height the image is allowed to be.

    Returns:
        path to new file.

    Raises:
        ValueError: If the provided path is not a cover
    """
    orig, _ = os.path.splitext(path)
    if orig[-5:] != 'cover':
        raise ValueError('Provided path is not a cover?')

    target = f"{orig}.jpg"
    mid = f"{orig}.new.jpg"

    return _convert_and_resize(path, mid, target, max_height, 'RGB')


def discart_fix(path: str, max_height: int) -> str:
    """Converts and resizes discart

    Converts discart.[ext] to discart.png and resizes it to `max_height`,
    maintaining aspect ratio.

    Args:
        path: Path to discart.[ext]
        max_height: The max height the image is allowed to be.

    Returns:
        path to new file.

    Raises:
        ValueError: If the provided path is not a discart.
    """
    orig, _ = os.path.splitext(path)
    if orig[-7:] != 'discart':
        raise ValueError('Provided path is not a discart?')

    target = f"{orig}.png"
    mid = f"{orig}.new.png"

    return _convert_and_resize(path, mid, target, max_height, 'RGBA')


def image_find(path: str, image_name: str) -> str:
    """Checks if an image.[ext] exists in `path`

    Args:
        path: Directory to check for image.[ext] in.
        image_name: Name of image to look for without extension.

    Returns:
        Name of image.[ext] file if one is found, blank otherwise.
    """
    LOGGER.debug("Searching for %s.ext in: %s", image_name, path)
    with fops.pushd(path):
        for image_ext in ('jpg', 'png', 'webp', 'gif'):
            image_file = f'{image_name}.{image_ext}'
            if os.path.isfile(image_file):
                return image_file

    return ''


def process_dir_images(cover_image: str, folder_image: str, discart_image: str, image_height: int) -> Tuple[str, str]:
    """Processes images in album directory

    Args:
        cover_image: Name of cover image. (Typically cover.jpg)
        folder_image:  Name of folder image. (Typically folder.jpg)
        discart_image: Name of discart image. (Typically discart.png)
        image_height: The height that images should be resized to. (Maintaining aspect ratio.)

    Returns:
        A tuple with two strings
        tuple[0] = path to cover.jpg
        tuple[1] = path to discart.png (empty if no discart_image was specified)
    """
    fops.delete(folder_image)

    new_cover = cover_fix(cover_image, image_height)
    if cover_image != new_cover:
        fops.delete(cover_image)

    new_discart = ''
    if discart_image:
        new_discart = discart_fix(discart_image, image_height)
        if discart_image != new_discart:
            fops.delete(discart_image)

    return new_cover, new_discart
