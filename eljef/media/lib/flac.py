# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""FLAC File Manipulation"""

import logging

from typing import (Any, Tuple)

# noinspection PyProtectedMember
from mutagen.flac import (Picture, FLAC)

from eljef.core.strings import makestr
from eljef.media.lib.nfo import album_nfo_base

LOGGER = logging.getLogger(__name__)

__FID_ALBUM_ARTIST = 'album_artist'
__FID_ALBUM_TITLE = 'album'
__FID_DATE_ORIG_RELEASE = 'originaldate'
__FID_DATE_RELEASE = 'date'
__FID_MB_ALBUM_ID = 'musicbrainz_albumid'
__FID_MB_ALBUM_TYPE = 'musicbrainz_albumtype'
__FID_MB_ARTIST_ID = 'musicbrainz_albumartistid'
__FID_MB_RELEASE_GROUP_ID = 'musicbrainz_releasegroupid'
__FID_PUBLISHER = 'publisher'


class FLACFix:
    """Fixes some issues in FLAC files after importing with beets.

    Attributes:
        file = File being operated on
        flac = FLAC tags object for the file
    """
    def __init__(self, file: str) -> None:
        self.file = file
        LOGGER.debug("Reading FLAC tags from %s", file)
        self.flac = FLAC(file)

    def add_picture(self, picture_path: str) -> None:
        """Adds a picture to the FLAC file.

        Args:
            picture_path: Path to the picture to embed.

        Note:
            This assumes the picture is the album cover.
            This assumes the picture is a jpeg file.
        """
        image = Picture()
        image.desc = 'front cover'
        image.mime = 'image/jpeg'
        image.type = 3

        with open(picture_path, 'rb') as picture_file:
            image.data = picture_file.read()

        self.flac.add_picture(image)

    def clear_pictures(self) -> None:
        """Clears all picture data from the tags."""
        self.flac.clear_pictures()

    def fix_album_type(self) -> None:
        """Recent versions of beets convert the albumtype and musicbrainz_albumtype tags to lists.
           This converts it back to a string.
        """
        musicbrainz_albumtype = self.flac.get('musicbrainz_albumtype')
        release_type = self.flac.get('releasetype')
        if musicbrainz_albumtype:
            self.flac['musicbrainz_albumtype'] = self._list_to_string(musicbrainz_albumtype)
        if release_type:
            self.flac['releasetype'] = self._list_to_string(release_type)

    @staticmethod
    def _list_to_string(tag_data: Any) -> str:
        """Converts a list, set, or tuple to a string

        Args:
            tag_data: list, set, or tuple to convert to string
        """
        if isinstance(tag_data, (bytes, str)):
            return makestr(tag_data)
        if isinstance(tag_data, (list, set, tuple)):
            return ''.join(tag_data)

        raise TypeError(f"data is not type of bytes, str, list, set, tuple -> type is {type(tag_data)}")

    def save(self) -> None:
        """Saves all edits to the FLAC data."""
        self.flac.save()

    def set_reference_loudness(self, volume: float) -> None:
        """Sets the replaygain_reference_loudness tag.

        Args:
            volume: Decibel level used for the replaygain volume reference
        """
        if volume and volume > 1:
            self.flac['replaygain_reference_loudness'] = f"{volume} dB"


def _mb_tags_from_flac(path: str, tag_data: FLAC) -> Tuple[str, str, str, str]:
    """Returns Musicbrainz Identifiers

    Args:
        path: path to MP3 file to read tags from
        tag_data: FLAC tag object

    Returns:
        A list of Musicbrainz identifiers
        0 -> Musicbrainz Release Group ID
        1 -> Musicbrainz Artist ID
        2 -> Musicbrainz Album Type
        3 -> Musicbrainz Album Artist Credit
    """
    LOGGER.debug("Retrieving MusicBrainz tags from %s", path)

    release_group_id = str(tag_data.get(__FID_MB_RELEASE_GROUP_ID, ''))
    artist_id = str(tag_data.get(__FID_MB_ALBUM_ID, ''))
    album_type = str(tag_data.get(__FID_MB_ALBUM_TYPE, ''))
    artist_credits = str(tag_data.get(__FID_MB_ARTIST_ID, ''))

    return release_group_id, artist_id, album_type, artist_credits


def _release_date_from_flac(path: str, tag_data: FLAC) -> str:
    """Returns a formatted release date string.

    Args:
        path: path to MP3 file to read tags from
        tag_data: mutagen ID3 tags dictionary

    Returns:
        A formatted release date string.
    """
    LOGGER.debug("Retrieving Date tags from %s", path)

    if __FID_DATE_ORIG_RELEASE in tag_data:
        return str(tag_data[__FID_DATE_ORIG_RELEASE])
    if __FID_DATE_RELEASE in tag_data:
        return str(tag_data[__FID_DATE_RELEASE])

    return '0000-00-00'


def get_album_nfo(path: str) -> dict:
    """Builds an album NFO dictionary

    Args:
        path: Path to FLAC file to build NFO data from

    Returns:
        A dictionary of NFO data to be written to a file
    """
    LOGGER.debug("Reading vorbis tags from %s", path)
    flac_data = FLAC(path)

    publisher = ''
    if __FID_PUBLISHER in flac_data:
        publisher = str(flac_data[__FID_PUBLISHER])

    release_group_id, artist_id, album_type, artist_credits = _mb_tags_from_flac(path, flac_data)

    ret = album_nfo_base(str(flac_data[__FID_ALBUM_TITLE]), str(flac_data[__FID_ALBUM_ARTIST]),
                         _release_date_from_flac(path, flac_data), publisher, mb_release_group=release_group_id,
                         mb_artist_id=artist_id, mb_album_type=album_type, mb_artist_credits=artist_credits)

    return ret
