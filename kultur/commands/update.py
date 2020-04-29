from kultur.update import data


def update_program():
    """
    Update the complete program.

    This will scrape the new program from the web,
    and each successful program update (per theater)
    will replace an old program if present.
    """
    updated_theaters = data.update_program_all_theaters()
    data.replace_records(updated_theaters)
