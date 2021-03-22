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
import mimetypes

from typing import Tuple

import mutagen
import mutagen.apev2
import mutagen.id3

# noinspection PyPackageRequirements,PyUnresolvedReferences
from gi.repository import GLib
from rgain3 import (rgcalc, rgio, util)

LOGGER = logging.getLogger(__name__)


__CMD_MP3GAIN = ['mp3gain', '-a', '-c', '-r']

__DEFAULT_TRACK_GAIN = float(89)

__FID_ALBUM_ARTIST = 'TPE2'
__FID_ALBUM_TITLE = 'TALB'
__FID_APIC = 'APIC:'
__FID_DATE_ORIG_RELEASE = 'TDOR'
__FID_DATE_RECORDED = 'TDRC'
__FID_DATE_RELEASE = 'TDRL'
__FID_MB_ALBUM_ID = 'TXXX:MusicBrainz Artist Id'
__FID_MB_ALBUM_TYPE = 'TXXX:MusicBrainz Album Type'
__FID_MB_ARTIST_ID = 'TXXX:MusicBrainz Artist Id'
__FID_MB_RELEASE_GROUP_ID = 'TXXX:MusicBrainz Release Group Id'
__FID_PUBLISHER = 'TPUB'
__FID_RELATIVE_VOLUME_ALBUM = 'RVA2:album'
__FID_RELATIVE_VOLUME_TRACK = 'RVA2:track'
__FID_REPLAYGAIN_ALBUM_GAIN = 'TXXX:replaygain_album_gain'
__FID_REPLAYGAIN_ALBUM_PEAK = 'TXXX:replaygain_album_peak'
__FID_REPLAYGAIN_Q_REF_LOUD = 'TXXX:QuodLibet::replaygain_reference_loudness'
__FID_REPLAYGAIN_REF_LOUD = 'TXXX:replaygain_reference_loudness'
__FID_REPLAYGAIN_TRACK_GAIN = 'TXXX:replaygain_track_gain'
__FID_REPLAYGAIN_TRACK_PEAK = 'TXXX:replaygain_track_peak'

__XML_ID_ALBUM = 'album'
__XML_ID_ALBUM_ARTIST_CREDITS = 'albumArtistCredits'
__XML_ID_ALBUM_TYPE = 'type'
__XML_ID_ARTIST = 'artist'
__XML_ID_ARTIST_DESC = 'artistdesc'
__XML_ID_MB_ALBUM_ID = 'musicbrainzalbumid'
__XML_ID_MB_ARTIST_ID = 'musicBrainzArtistID'
__XML_ID_MB_RELEASE_GROUP_ID = 'musicbrainzreleasegroupid'
__XML_ID_LABEL = 'label'
__XML_ID_RELEASE_DATE = 'releasedate'
__XML_ID_SCRAPEDMBID = 'scrapedmbid'
__XML_ID_TITLE = 'title'

__REPLAYGAIN_FRAMES_FOR_COMP = (__FID_RELATIVE_VOLUME_ALBUM.lower(), __FID_RELATIVE_VOLUME_TRACK.lower(),
                                __FID_REPLAYGAIN_ALBUM_GAIN.lower(), __FID_REPLAYGAIN_ALBUM_PEAK.lower(),
                                __FID_REPLAYGAIN_Q_REF_LOUD.lower(), __FID_REPLAYGAIN_REF_LOUD.lower(),
                                __FID_REPLAYGAIN_TRACK_GAIN.lower(), __FID_REPLAYGAIN_TRACK_PEAK.lower())

__REPLAYGAIN_FRAMES_FOR_CASE = (__FID_REPLAYGAIN_ALBUM_GAIN.lower(), __FID_REPLAYGAIN_ALBUM_PEAK.lower(),
                                __FID_REPLAYGAIN_TRACK_GAIN.lower(), __FID_REPLAYGAIN_TRACK_PEAK.lower())


def _album_nfo_from_file_date_tags(path: str, tag_data: mutagen.id3.ID3) -> str:
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
    if __FID_DATE_RECORDED in tag_data:
        return str(tag_data[__FID_DATE_RECORDED])

    return '0000-00-00'


def _album_nfo_from_file_mb_tags(path: str, tag_data: mutagen.id3.ID3, nfo_data: dict) -> dict:
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

    for mp3_fid, xml_id in ((__FID_MB_RELEASE_GROUP_ID, __XML_ID_MB_RELEASE_GROUP_ID),
                            (__FID_MB_ALBUM_ID, __XML_ID_MB_ALBUM_ID),
                            (__FID_MB_ALBUM_TYPE, __XML_ID_ALBUM_TYPE)):
        if mp3_fid in tag_data:
            ret[__XML_ID_ALBUM][xml_id] = str(tag_data[mp3_fid])

    if __FID_MB_ARTIST_ID in tag_data:
        ret[__XML_ID_ALBUM][__XML_ID_ALBUM_ARTIST_CREDITS][__XML_ID_MB_ARTIST_ID] = str(tag_data[__FID_MB_ARTIST_ID])

    return ret


def album_nfo_from_file(path: str) -> dict:
    """Returns a dictionary of NFO data

    Args:
        path: path to MP3 file to read tags from

    Note:
        It is assumed that the MP3 file to be read has been processed by beets.
    """
    LOGGER.debug("Reading MP3 tags from %s", path)
    mp3 = mutagen.File(path)

    ret = {
        __XML_ID_ALBUM: {
            __XML_ID_TITLE: str(mp3.tags[__FID_ALBUM_TITLE]),
            __XML_ID_ARTIST_DESC: str(mp3.tags[__FID_ALBUM_ARTIST]),
            __XML_ID_SCRAPEDMBID: True,
            __XML_ID_RELEASE_DATE: _album_nfo_from_file_date_tags(path, mp3.tags),
            __XML_ID_ALBUM_ARTIST_CREDITS: {
                __XML_ID_ARTIST: str(mp3.tags[__FID_ALBUM_ARTIST]),
            }
        }
    }

    if __FID_PUBLISHER in mp3.tags:
        ret[__XML_ID_ALBUM][__XML_ID_LABEL] = str(mp3.tags[__FID_PUBLISHER])

    return _album_nfo_from_file_mb_tags(path, mp3.tags, ret)


def correct_replaygain_tags(path: str) -> None:
    """Make sure replaygain tags are lower case.

    TXXX tags are not supposed to be case insensitive. Some players suck and
    only read upper or lower case tags. Instead of forcing everything to upper,
    force everything to lower and check for upper case tags from players and
    report bugs to them.

    Args:
        path: path to mp3 file to correct tags for.
    """
    to_correct = []

    mp3 = mutagen.File(path)
    for key in mp3.tags.keys():
        if key.lower() in __REPLAYGAIN_FRAMES_FOR_CASE:
            to_correct.append(key)

    for key in to_correct:
        data = mp3.tags[key]
        data.desc = data.desc.lower()
        del mp3.tags[key]
        field_id, desc = key.split(":")
        new_key = f"{field_id.upper()}:{desc.lower()}"
        mp3.tags[new_key] = data

    mp3.save()


def fix_cover_tag(path: str, cover_image: str) -> None:
    """Replaces the cover image in the ID3 tag for an MP3.

    Args:
        path: path to MP3 file to replace tags on
        cover_image: Path to cover image to use in ID3 tags.
    """
    LOGGER.debug(" ** %s - Removing all images", path)
    mp3_data = mutagen.File(path)

    if __FID_APIC in mp3_data.tags.keys():
        del mp3_data.tags[__FID_APIC]

    LOGGER.debug(" ** %s - Adding front cover image", path)
    mime_type = mimetypes.guess_type(cover_image)[0]
    with open(fr'{cover_image}', 'rb') as cover_rb:
        mp3_data.tags.add(mutagen.id3.APIC(mime=mime_type, type=mutagen.id3.PictureType.COVER_FRONT,
                                           data=cover_rb.read()))

    mp3_data.tags.update_to_v24()
    mp3_data.save()


def mp3gain(mp3s: list, target_gain: float, debug: bool) -> None:
    """Runs mp3gain on the provided list of mp3s

    Args:
        mp3s: list of mp3s to process
        target_gain: the target gain to adjust the track to
        debug: Print debug output

    Raises:
        ValueError: If target_gain is not float
        subprocess.CalledProcessError: If something goes wrong running mp3gain
    """
    if not isinstance(target_gain, float):
        raise ValueError(f"target_gain {target_gain} not float")
    if not isinstance(mp3s, list):
        raise TypeError("provided list of mp3s is not a list")

    new_target = target_gain - __DEFAULT_TRACK_GAIN
    if new_target > float(0):
        full_cmd = __CMD_MP3GAIN + ['-d', str(new_target)] + sorted(mp3s)
    else:
        full_cmd = __CMD_MP3GAIN + sorted(mp3s)

    LOGGER.debug(' '.join(full_cmd))
    try:
        subprocess.run(full_cmd, capture_output=not debug, check=True)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            LOGGER.error(error.stderr)
        elif error.stdout:
            LOGGER.error(error.stdout)
        raise


def remove_ape_tags(path: str) -> None:
    """Removes APE tags fro the MP3 file.

    Args:
        path: path to MP3 file to remove tags from
    """
    try:
        ape = mutagen.apev2.APEv2(path)
        ape.delete()
        ape.save()
    except mutagen.apev2.APENoHeaderError:
        pass


def remove_replaygain_tags(path: str) -> None:
    """Removes all previously stored replaygain tags.

    Args:
        path: path to mp3 file to remove tags from
    """
    to_remove = []

    mp3 = mutagen.File(path)
    for key in mp3.tags.keys():
        if key.lower() in __REPLAYGAIN_FRAMES_FOR_COMP:
            to_remove.append(key)

    for key in to_remove:
        del mp3.tags[key]

    mp3.save()


def _replaygain_calc(mp3s: list, target_gain: float) -> Tuple[dict, rgcalc.GainData]:
    """Calculate replaygain values for all provided files.

    Args:
        mp3s: list of mp3s to process
        target_gain: the target gain to adjust the track to

    Returns:
        Replaygain values for all files
    """
    exc_slot = [None]

    # Handlers
    # noinspection PyUnusedLocal
    def on_loop_finished(evsrc, trackdata, albumdata):  # pylint: disable=unused-argument
        loop.quit()

    # noinspection PyUnusedLocal
    def on_track_started(evsrc, filename):  # pylint: disable=unused-argument
        LOGGER.debug(" ** replaygain started: %s", filename)

    # noinspection PyUnusedLocal
    def on_track_finished(evsrc, filename, gaindata):  # pylint: disable=unused-argument
        LOGGER.debug(" ** replaygain stopped: %s", filename)

    # noinspection PyUnusedLocal
    def on_error(evsrc, exc):  # pylint: disable=unused-argument
        exc_slot[0] = exc
        loop.quit()

    replaygain_values = rgcalc.ReplayGain(mp3s, True, int(round(target_gain)))
    with util.gobject_signals(replaygain_values,
                              ("all-finished", on_loop_finished),
                              ("track-started", on_track_started),
                              ("track-finished", on_track_finished),
                              ("error", on_error),):
        loop = GLib.MainLoop()
        replaygain_values.start()
        loop.run()

    if exc_slot[0] is not None:
        raise exc_slot[0]  # pylint: disable=raising-bad-type

    return replaygain_values.track_data, replaygain_values.album_data


def replaygain(mp3s: list, target_gain: float) -> None:
    """Calculates and writes replaygain data to ID3 tag.

    Args:
        mp3s: list of mp3s to process
        target_gain: the target gain to adjust the track to
    """
    forms_map = rgio.BaseFormatsMap(None)
    tracks_data, album_data = _replaygain_calc(mp3s, target_gain)

    for filename, track_data in tracks_data.items():
        forms_map.write_gain(filename, track_data, album_data)
