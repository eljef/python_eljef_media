# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Beet FLAC CLI Program Main Functionality"""

import logging
import os

from pathlib import Path

from eljef.core import (applog, cli, fops)
from eljef.media.__version__ import VERSION
from eljef.media.cli.__beet_flac_args__ import CMD_LINE_ARGS
from eljef.media.cli.__beet_flac_vars__ import (DESCRIPTION, NAME)
from eljef.media.cli.__common_audio__ import process_album_dir
from eljef.media.lib.cli import (ALBUM_NFO, album_dir_finish, check_media_dir, exit_with_error, get_media_dirs)
from eljef.media.lib.flac import (get_album_nfo, FLACFix)

LOGGER = logging.getLogger()


def _check_beets_config(path: str) -> None:
    """Checks if the specified beets configuration file exists.

    Args:
        path: path to the beets configuration file
    """
    if not path:
        return

    if not os.path.exists(path):
        exit_with_error(f"Specified beets configuration file does not exist: {path}")

    check_file = path
    if os.path.islink(path):
        check_file = os.readlink(path)

    if not os.path.isfile(check_file):
        exit_with_error(f"Specified beets configuration file is not a file or link to a file: {path}")


def _get_beets_gain_level(path: str) -> float:
    """Returns the replay gain volume level to set in the FLAC tags.

    Args:
        path: Path to the beets configuration file containing replaygain settings.
    """
    target_volume = 89.0
    default_beets_config = os.path.join(str(Path.home()), '.config/beets/config.yaml')

    if not path and not os.path.exists(default_beets_config):
        return target_volume

    if not path:
        path = default_beets_config

    config_data = fops.file_read_convert(path, fops.YAML, default=True)
    target_level = config_data.get('replaygain', {}).get('targetlevel')
    if target_level:
        target_volume = float(target_level)

    return target_volume


def _process_flac_files(flac_list: list, cover_image: str, target_volume: float) -> list:
    """Process individual FLAC files

    Args:
        flac_list: List of FLAC files to process
        cover_image: Name of the image to use for the front cover.
        target_volume: Volume, in decibels, to set reference volume to.

    Returns:
        A list of fixed flac objects
    """
    ret = []
    LOGGER.info("   ** Correcting tags and images")
    for flac_file in flac_list:
        flac_to_fix = FLACFix(flac_file)
        flac_to_fix.fix_album_type()
        flac_to_fix.clear_pictures()
        flac_to_fix.add_picture(cover_image)
        flac_to_fix.set_reference_loudness(target_volume)
        flac_to_fix.save()
        ret.append(flac_to_fix)

    return ret


def _process_flac_dir(base: str, path: str, image_height: int, target_volume: float, **kwargs) -> None:
    """Main FLAC directory processing function.

    Args:
        base: Base path holding directories of FLACs (Artist Directory)
        path: Sub-directory holding FLACs (Album Directory)
        image_height: The height that cover.jpg should be resized to.
        target_volume: Volume, in decibels, to set reference volume to.

    Keyword Args:
        debug (bool): Enable debug logging when True
        ignore_folder (bool): Ignore the presence of folder.jpg
    """
    f_data = process_album_dir(base, path, image_height, kwargs.get('ignore_folder', False), 'flac')
    if f_data.skip:
        return

    with fops.pushd(f_data.full_path):
        fixed_flac_objs = _process_flac_files(f_data.flac_list, f_data.cover_image, target_volume)
        nfo_data = get_album_nfo(fixed_flac_objs[0])
        album_dir_finish(ALBUM_NFO, nfo_data)


def main(**kwargs) -> None:
    """Main Beet FLAC functionality.

    Keyword Args:
        beets_config (str): Path to beets configuration file.
        debug (bool): If True, enables debug logging.
        directory (str): Path to directory to process.
        ignore_folder (bool): Ignore the existence of folder.jpg
        image_height (int): Max image height for resized images.
    """
    directory = kwargs.get('directory')
    flac_dirs = get_media_dirs(directory, 'flac', 'No FLAC files found')

    target_volume = _get_beets_gain_level(kwargs.get('beets_config'))

    for dir_to_process in sorted(flac_dirs):
        _process_flac_dir(directory, dir_to_process, kwargs.get('image_height'), target_volume,
                          ignore_folder=kwargs.get('ignore_folder'))


def cli_main() -> None:
    """Main functionality when run from CLI."""
    args = cli.args_simple(NAME, DESCRIPTION, CMD_LINE_ARGS)

    if args.version_out:
        cli.print_version(NAME, VERSION)

    applog.setup_app_logging(args.debug_log, args.log_file)

    if args.max_image_height < 1:
        exit_with_error(f"Max image height must be greater than 0. Specified {args.max_image_height}")

    _check_beets_config(args.beets_config)

    dir_to_process = check_media_dir(args.flac_directory)

    LOGGER.info("Processing: %s", args.flac_directory)
    main(beets_config=args.beets_config, debug=args.debug_log, directory=dir_to_process,
         ignore_folder=args.ignore_folder, image_height=args.max_image_height)


if __name__ == '__main__':
    cli_main()
