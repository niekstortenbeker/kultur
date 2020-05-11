from typing import Union


def default_time(context) -> str:
    return (
        context.get_current_parameters()["date_time"]
        .to("Europe/Berlin")
        .format("HH:mm")
    )


def default_day(context) -> str:
    return (
        context.get_current_parameters()["date_time"]
        .to("Europe/Berlin")
        .format("ddd D.M.", locale="de")
        .upper()
    )


def default_description_start(context) -> Union[str, None]:
    """slice description shorter, try to do so at a logical point in the sentence"""
    desc: Union[str, None] = context.get_current_parameters()["description"]
    if not desc:
        return desc
    if len(desc) < 300:
        return desc

    desc = desc[0:300]

    last_dot = desc.rfind(".")
    if last_dot > 150:
        return desc[0 : last_dot + 1]

    last_semi_colon = desc.rfind(";")
    if last_semi_colon > 150:
        return desc[0 : last_semi_colon + 1]

    last_comma = desc.rfind(",")
    if last_comma > 150:
        return desc[0 : last_comma + 1]

    return desc[0:250]


def default_description_end(context) -> Union[str, None]:
    """if description_start did not fit all the text, store remainder"""
    desc = context.get_current_parameters()["description"]
    desc_start = context.get_current_parameters()["description_start"]
    if not desc:
        return None
    elif len(desc) == len(desc_start):
        return None
    else:
        return desc[len(desc_start) :]


def default_location_name_url(context) -> str:
    return context.get_current_parameters()["location"].replace(" ", "").lower()
