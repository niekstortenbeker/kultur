import re

from data.show import Show
from update.services.metainfo import MetaInfo


def is_dubbed(show: Show, meta_info: MetaInfo) -> bool:
    """
    for a movie, test if it is probably dubbed

    returns False if a film has:
        - a string in Show.language_version
        - a German Speaking country in MetaInfo().country AND
            - no title info OR
            - MetaInfo().title == MetaInfo().original_title
    """
    if show.language_version:  # OMUs and OV
        return False
    elif _is_german(meta_info):
        return False
    else:
        return True


def _is_german(show_metainfo: MetaInfo) -> bool:
    if not show_metainfo:
        raise AttributeError("No meta info found")
    country = show_metainfo.country
    if not country:  # assuming it's dubbed
        return False
    if not re.search("deutschland|sterreich|schweiz", country.lower()):
        return False
    title = show_metainfo.title
    title_original = show_metainfo.title_original
    if not title_original:  # if no original title info is available
        return True
    elif title.strip().lower() == title_original.strip().lower():
        return True
    else:  # a different original title suggests it is dubbed after all
        return False
