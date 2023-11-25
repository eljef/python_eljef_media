# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Common CLI Audio Functionality"""
import logging
import os

from eljef.core import fops
from eljef.core.dictobj import DictObj
from eljef.media.lib import image

LOGGER = logging.getLogger()


def process_album_dir(base: str, path: str, image_height: int, ignore_folder: bool, fext: str) -> DictObj:
    """Main album directory processing function.

    Args:
        base: Base path holding directories of audio files. (Artist Directory)
        path: Sub-directory holding audio files. (Album Directory)
        image_height: The height that cover.jpg should be resized to.
        ignore_folder (bool): Ignore the presence of folder.jpg
        fext: File extension to filter in folder

    Note:
        If `folder.ext` exists and ignore_folder is not true, returns with `ret.skip` = True
        If not `cover.ext` exists, returns with `ret.skip` = True

    Returns:
        DictObj with the following set.
        cover_image: name of the file to be used as the cover_image (cover.jpg)
        file_list: list of files found with extension from `fext`
        full_path: full path to the album directory
        skip: True if conditions mentioned above were met
    """
    full_path = os.path.join(base, path)
    LOGGER.debug("Processing: %s", full_path)
    LOGGER.info(" * %s", path)

    file_list = sorted(fops.list_files_by_extension(full_path, fext))

    folder_image = image.image_find(full_path, 'folder')
    if folder_image and not ignore_folder:
        LOGGER.warning("   ** %s found: Skipping because already processed", folder_image)
        return DictObj({'skip': True})

    cover_image = image.image_find(full_path, 'cover')
    discart_image = image.image_find(full_path, 'discart')
    if not cover_image:
        LOGGER.error("   ** No cover image found: Skipping.")
        return DictObj({'skip': True})

    with fops.pushd(full_path):
        cover_image, _ = image.process_dir_images(cover_image, folder_image, discart_image, image_height)

    return DictObj({
        'cover_image': cover_image,
        'file_list': file_list,
        'full_path': full_path,
        'skip': False
    })
