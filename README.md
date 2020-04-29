# kultur
### Collect and combine programs from theaters in Bremen
This command line tool collects the program of theaters I like in bremen. It filters out dubbed movies (because who likes those?), and then combines the programs to one sorted-by-date overview. 


### Installation
If you don't have a distribution, create this first. Download the source code, and go to the project directory. Then run:   
`$ python setup.py sdist`
  
Then pip install the distribution:  
`$ pip install dist/kultur--_version_.tar.gz`

### Usage 
#### cli
Display this week's program that was stored on disk:    
`$ kultur`  
  
Display a new program (uses web scraping):  
`$ kultur -n`

Display only today:  
`$ kultur -t`

#### api
```
>>> import kultur
>>> kultur.init_database()
>>> kultur.print_today()
There are no shows to display
>>> kultur.update_program()
(...)
>>> kultur.print_today()
(...)
>>> import arrow
>>> kultur.get_shows(arrow.now(), arrow.now().shift(weeks=+1), "all", False)
[Show(Theater Bremen, Schäfchen im Trockenen), (...)]
```

**functions**  

* _init_database():_  
* _update_program():_   
* _get_shows(start, stop, category, dubbed)_  
* _print_header()_
* _print_today()_  
* _print_week()_  
