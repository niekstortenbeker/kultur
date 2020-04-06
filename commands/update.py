from update import data


def update_program():
    """Scrape the new program from the web, replaces program on database"""
    updated_theaters = data.update_program_all_theaters()
    data.replace_records(updated_theaters)
