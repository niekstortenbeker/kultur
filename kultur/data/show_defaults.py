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
    description = context.get_current_parameters()["description"]
    return make_description_start(description)


def make_description_start(description: str) -> Union[str, None]:
    if not description:
        return description
    if len(description) < 300:
        return description

    desc = description[0:300]

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
    description = context.get_current_parameters()["description"]
    description_start = context.get_current_parameters()["description_start"]
    return make_description_end(description, description_start)


def make_description_end(description: str, description_start) -> Union[str, None]:
    if not description:
        return None
    elif len(description) == len(description_start):
        return None
    else:
        return description[len(description_start) :]


def default_location_name_url(context) -> str:
    return context.get_current_parameters()["location"].replace(" ", "").lower()
