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
# mp3.py : ElJef MP3 File Manipulation
"""ElJef MP3 File Manipulation."""

import logging
import subprocess

from typing import Union

import eyed3
from eyed3 import mimetype
from eyed3.id3 import TagFile
from eyed3.id3.tag import (ID3_V2_4, Tag)
from eyed3.mp3 import Mp3AudioFile

LOGGER = logging.getLogger(__name__)

__CMD_BEET_REPLAYGAIN = ['beet', 'replaygain']
__CMD_BEET_UP = ['beet', 'up']
__CMD_MP3GAIN = ['mp3gain', '-c', '-r']

__DEFAULT_TRACK_GAIN = float(89)

__RPG_FID = b"RGAD"


def _album_nfo_from_file_date_tags(path: str, tag_data: Tag) -> str:
    """Returns a formatted release date string.

    Args:
        path: path to MP3 file to read tags from
        tag_data: ID3 tag object

    Returns:
        A formatted release date string.
    """
    LOGGER.debug("Retrieving Date tags from %s", path)

    date_data = tag_data.getBestDate()

    release = date_data.year
    if date_data.month:
        release = f"{release}-{date_data.month:02}"
    if date_data.day:
        release = f"{release}-{date_data.day:02}"

    return release


def _album_nfo_from_file_mb_tags(path: str, tag_data: Tag, nfo_data: dict) -> dict:
    """Returns a dictionary that includes MusicBrainz info

    Args:
        path: path to MP3 file to read tags from
        tag_data: ID3 tag object
        nfo_data: Dictionary of data to be used for generating a NFO file.

    Returns:
        A dictionary suitable for usage in generating a NFO file.
    """
    LOGGER.debug("Retrieving MusicBrainz tags from %s", path)

    ret = nfo_data

    mb_rg_id = tag_data.user_text_frames.get('MusicBrainz Release Group Id')
    mb_album_id = tag_data.user_text_frames.get('MusicBrainz Album Id')
    mb_album_type = tag_data.user_text_frames.get('MusicBrainz Album Type')
    mb_artist_id = tag_data.user_text_frames.get('MusicBrainz Album Artist Id')

    if mb_rg_id and mb_rg_id.text:
        ret['album']['musicbrainzreleasegroupid'] = mb_rg_id.text

    if mb_album_id and mb_album_id.text:
        ret['album']['musicbrainzalbumid'] = mb_album_id.text

    if mb_album_type and mb_album_type.text:
        ret['album']['type'] = mb_album_type.text

    if mb_artist_id and mb_artist_id.text:
        ret['album']['albumArtistCredits']['musicBrainzArtistID'] = mb_artist_id.text

    return ret


def album_nfo_from_file(path: str) -> dict:
    """Returns a dictionary of NFO data

    Args:
        path: path to MP3 file to read tags from

    Note:
        It is assumed that the MP3 file to be read has been processed by beets.
    """
    LOGGER.debug("Reading MP3 tags from %s", path)
    mp3 = eyed3.load(path)

    ret = {
        'album': {
            'title': mp3.tag.album,
            'artistdesc': mp3.tag.album_artist,
            'scrapedmbid': True,
            'releasedate': _album_nfo_from_file_date_tags(path, mp3.tag),
            'albumArtistCredits': {
                'artist': mp3.tag.album_artist,
            }
        }
    }

    if mp3.tag.publisher:
        ret['album']['label'] = mp3.tag.publisher

    return _album_nfo_from_file_mb_tags(path, mp3.tag, ret)


def beet_replaygain_album(artist: str, album: str, debug: bool) -> None:
    """Run 'beet replaygain' on an Album.

    Args:
        artist: Name of artist to run 'beet replaygain' on.
        album: Name of album to run 'beet replaygain' on.
        debug: Print debug output.
    """
    full_cmd = __CMD_BEET_REPLAYGAIN + [artist, album]

    LOGGER.debug(' '.join(full_cmd))
    try:
        subprocess.run(full_cmd, capture_output=not debug, check=True)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            LOGGER.error(error.stderr)
        elif error.stdout:
            LOGGER.error(error.stdout)
        raise


def beet_up(debug: bool) -> None:
    """Run 'beet up' on an Album.

    Args:
        debug: Print debug output.
    """
    LOGGER.debug(' '.join(__CMD_BEET_UP))
    try:
        subprocess.run(__CMD_BEET_UP, capture_output=not debug, check=True)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            LOGGER.error(error.stderr)
        elif error.stdout:
            LOGGER.error(error.stdout)
        raise


def fix_cover_tag(path: str, cover_image: str, mp3_data: Union[Mp3AudioFile, TagFile]) -> None:
    """Replaces the cover image in the ID3 tag for an MP3.

    Args:
        path: path to MP3 file to replace tags on
        cover_image: Path to cover image to use in ID3 tags.
        mp3_data: MP3 data from eyed3
    """
    LOGGER.debug(" ** %s - Removing all images", path)
    if eyed3.id3.frames.IMAGE_FID in mp3_data.tag.frame_set:
        del mp3_data.tag.frame_set[eyed3.id3.frames.IMAGE_FID]

    LOGGER.debug(" ** %s - Adding front cover image", path)
    mime_type = mimetype.guessMimetype(cover_image)
    with open(fr'{cover_image}', 'rb') as cover_rb:
        mp3_data.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, cover_rb.read(), mime_type, "Front Cover")

    mp3_data.tag.save(version=ID3_V2_4)


def track_mp3gain(path: str, target_gain: float, debug: bool) -> Union[Mp3AudioFile, TagFile]:
    """Runs mp3gain on the provided `path`

    This will run mp3gain on the provided `path`, adjusting the suggested gain
    by the provided value, and then applying the track gain.

    Args:
        path: path to MP3 file to calculate track gain for
        target_gain: the target gain to adjust the track to
        debug: Print debug output

    Raises:
        ValueError: If target_gain is not float
        subprocess.CalledProcessError: If something goes wrong running mp3gain

    Returns:
        ID3 Tag Object with replay gain tags removed.
    """
    if not isinstance(target_gain, float):
        raise ValueError(f"target_gain {target_gain} not float")

    new_target = target_gain - __DEFAULT_TRACK_GAIN
    if new_target > float(0):
        full_cmd = __CMD_MP3GAIN + ['-d', str(new_target), path]
    else:
        full_cmd = __CMD_MP3GAIN + [path]

    LOGGER.debug(' '.join(full_cmd))
    try:
        subprocess.run(full_cmd, capture_output=not debug, check=True)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            LOGGER.error(error.stderr)
        elif error.stdout:
            LOGGER.error(error.stdout)
        raise

    mp3 = eyed3.load(path)
    if __RPG_FID in mp3.tag.frame_set:
        del mp3.tag.frame_set[__RPG_FID]

    return mp3
