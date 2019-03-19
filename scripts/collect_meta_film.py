search_term = 'Perfect Blue'
url = 'https://www.vpro.nl/cinema/zoek.html?q=' + search_term

# get html

result = soup.find('list', class_='vas-result')
title = result.find('h1').text.strip()
# check if it matches the expected title
# check if the date matches
# if these things are correct, save number of stars and hyperlink to cinema.nl article
