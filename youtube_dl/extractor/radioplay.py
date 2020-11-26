# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    unified_strdate,
)


class RadioplayIE(InfoExtractor):
    IE_DESC = 'radioplay.fi'
    _VALID_URL = r'https?://(?:www\.|kuuntele\.)?radioplay\.fi/(?:podcast/[^/]*/listen/)?(?P<id>\d+)/?'
    _TESTS = [
        {
            'url': 'https://radioplay.fi/podcast/auta-antti/listen/15723/',
            'md5': 'c21ef05387c9f46ad0d652b23a8bca69',
            'info_dict': {
                'id': '15723',
                'ext': 'mp3',
                'title': 'Ystävyydestä',
                'description': 'md5:17b9893c3ad4b05360eb1dd3efd13a0c',
                'thumbnail': r're:^https?://.*\.jpg$',
                'duration': 3176,
                'upload_date': '20190405',
                'age_limit': 0,
                'season_number': 2,
                'episode_number': 3,
                'channel': 'Auta Antti!',
                'channel_id': '278',
            },
        },
        {
            'url': 'https://kuuntele.radioplay.fi/11062400',
            'md5': '1fdd4eb3257608ae25f614c2e6a27c63',
            'info_dict': {
                'id': '2035100',
                'ext': 'mp3',
                'title': 'Lihastohtori - Juha Hulmi',
                'description': 'md5:654f2990985f4142620a4e600d017eaa',
                'thumbnail': r're:^https?://.*\.jpg$',
                'duration': 3892,
                'upload_date': '20201113',
                'age_limit': 0,
                'season_number': 3,
                'episode_number': 14,
                'channel': 'Polkuporinat',
                'channel_id': '348',
            },
        },
    ]

    def _real_extract(self, url):
        url_id = self._match_id(url)

        urlformat2 = r'https?://(?:kuuntele\.)?radioplay\.fi/(?P<id>\d+)'
        if re.match(urlformat2, url):
            page = self._download_webpage(url, url_id)
            realurl = self._search_regex(
                r"desktopUrl\s*:\s*'(http.*)'",
                page, 'desktopUrl')
        else:
            realurl = url

        episode_id = self._match_id(realurl)
        webpage = self._download_webpage(realurl, episode_id)
        jtxt = self._search_regex(
            r'window\.__PRELOADED_STATE__\s*=\s*({.+})',
            webpage, 'nowPlaying')
        jtxt = jtxt.replace(r'\x', '')  # Stupid hack to fix json parsing
        _json = self._parse_json(jtxt, episode_id)
        ep = _json['player']['nowPlaying']
        ch = _json['podcastsApi']['data']['channel']

        assert str(ep['PodcastRadioplayId']) == episode_id

        return {
            'id': episode_id,
            'title': ep['PodcastTitle'],
            'description': ep.get('PodcastDescription', None),
            'thumbnail': ep.get('PodcastImageUrl', None),
            'duration': ep.get('PodcastDuration', None),
            'upload_date': unified_strdate(ep.get('PodcastPublishDate', None)),
            'age_limit': 18 if ep.get('PodcastExplicit', 0) != 0 else 0,
            'season_number': ep.get('PodcastSeasonNumber', None),
            'episode': ep['PodcastTitle'],
            'episode_number': ep.get('PodcastEpisodeNumber', None),
            'channel': ch.get('PodcastChannelTitle', None),
            'channel_id': str(ch['PodcastChannelId']),
            'formats': [{
                'format_id': 'audio',
                'url': ep['PodcastExtMediaUrl'],
                'vcodec': 'none',
            }]
        }
