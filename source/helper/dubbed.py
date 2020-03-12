import re


def _is_german(show_metainfo):
    """
    evaluates if the movie is likely to be german

    movie is considered german when it's made in a german speaking country
    and the title and original title are equal

    Parameters
    ----------
    title: str
        title of a show (as used in Program() or MetaInfo())

    Raises
    ------
    AttributeError
        when no meta information is found

    Returns
    -------
    bool
        returns True when the movie is likely to be german
    """
    if not show_metainfo:
        raise AttributeError('No meta info found')
    country = show_metainfo.get("country")
    if not country:
        raise AttributeError('No meta info found')
    if re.search("deutschland|sterreich|schweiz", country.lower()):
        title = show_metainfo.get("title")
        title_original = show_metainfo.get("title_original")
        if not title_original:  # if no original title info is available
            return True
        elif title.strip().lower() == title_original.strip().lower():
            return True
        else:  # a different original title suggests it is dubbed after all
            return False
    else:
        return False


def film_is_probably_dubbed(show, show_metainfo):
    """
    evaluates if a movie is likely to be dubbed

    Movies that are Omu or OV etc are not dubbed, and movies that seem
    to be made in a german speaking country are considered not dubbed

    Parameters
    ----------
    show: dictionary
        a show dictionary (see Program())

    Returns
    -------
    bool
        True when film is probably dubbed
    """

    if show.get("language_version", False):  # OMUs and OV
        return False
    elif _is_german(show_metainfo):
        return False
    else:
        return True