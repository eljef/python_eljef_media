# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: 0BSD

"""Tag Names Used Everywhere"""

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


def album_nfo_base(album_title: str, album_artist: str, release_date: str, publisher: str, **kwargs) -> dict:
    """Returns a dictionary of NFO data

    Args:
        album_title: Album Title
        album_artist: Album Artist
        release_date: Release Date
        publisher: Publisher

    Keyword Args:
        mb_release_group: Musicbrainz Release Group
        mb_artist_id: Musicbrainz Arist ID
        mb_album_type: Musicbrainz Album Type
        mb_artist_credits: Musicbrainz Artist Credits

    Returns:
        Base NFO information
"""

    ret = {
        __XML_ID_ALBUM: {
            __XML_ID_TITLE: album_title,
            __XML_ID_ARTIST_DESC: album_artist,
            __XML_ID_SCRAPEDMBID: True,
            __XML_ID_RELEASE_DATE: release_date,
            __XML_ID_ALBUM_ARTIST_CREDITS: {
                __XML_ID_ARTIST: album_artist,
            }
        }
    }

    if publisher:
        ret[__XML_ID_ALBUM][__XML_ID_LABEL] = publisher
    if kwargs.get('mb_release_group'):
        ret[__XML_ID_ALBUM][__XML_ID_MB_RELEASE_GROUP_ID] = kwargs.get('mb_release_group')
    if kwargs.get('mb_artist_id'):
        ret[__XML_ID_ALBUM][__XML_ID_MB_ALBUM_ID] = kwargs.get('mb_artist_id')
    if kwargs.get('mb_album_type'):
        ret[__XML_ID_ALBUM][__XML_ID_ALBUM_TYPE] = kwargs.get('mb_album_type')
    if kwargs.get('mb_artist_credits'):
        ret[__XML_ID_ALBUM][__XML_ID_ALBUM_ARTIST_CREDITS][__XML_ID_MB_ARTIST_ID] = kwargs.get('mb_artist_credits')

    return ret
