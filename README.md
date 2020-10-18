# kultur
### Collect and combine programs from theaters in Bremen
This command line tool collects the program of theaters I like in bremen. It filters out dubbed movies (because who likes those?), and then combines the programs to one sorted-by-date overview. 


### Installation
* If you don't have a distribution, create this first. Download the source code, and go to the project directory. Then run:   
`$ python setup.py sdist`
  
* Then pip install the distribution:  
`$ pip install dist/kultur--_version_.tar.gz`

Kultur requires a set up postgreSQL database: 
* When necessary install postgreSQL (e.g. [postgresapp](https://postgresapp.com/) for macOS)
* Create a postgres user and database in the command line:
```
psql -U postgres
postgres=# CREATE DATABASE kultur;
CREATE DATABASE
postgres=# CREATE USER user_name WITH PASSWORD 'some_password';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE kultur TO user_name;
GRANT
```
* Create the environment variables 'kultur_database_user', 'kultur_database_password' and 'kultur_database_name' so that kultur can connect to the database. E.g. by adding these to the .bashrc file:  

```
export kultur_database_user="user_name"
export kultur_database_password="some_password"
export kultur_database_name="kultur"
```

### Usage 
#### cli
Display this week's program that was stored on disk:    
`$ kultur`  
  
Display a new program (uses web scraping):  
`$ kultur -n`

Display only today:  
`$ kultur -t`

Use fake data instead:  
`$ kultur -f`

#### api
```
>>> import kultur
>>> kultur.init_database()  # or kultur.init_fake_database()
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

* _init_database()_
* _init_fake_database()_
* _get_location_names()_  
* _update_program()_   
* _get_shows(start, stop, category, dubbed)_  
* _print_header()_
* _print_today()_  
* _print_week()_  
