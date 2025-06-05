# Sport Shop Project

## Google Allauth email configuration
[Google Allauth email configuration](https://console.cloud.google.com/auth/clients)


# Load [Leaderboard](leaderboard/fixtures) fixtures data
```shell
    python manage.py loaddata leaderboard/fixtures/game_fixtures.json
```


# Load [Product](products/fixtures) fixtures data
```shell
    python manage.py loaddata products/fixtures/categories.json products/fixtures/products.json products/fixtures/product_images.json
```

## Prerequisites
  - Python 3.10+
  - Virtualenv and Pip

## How to Run this Project    
  - Create a new project directory `mkdir sportshop`
  - Change directory to the project directory `cd sportshop`
  - create a virtual env `pip -m venv venv`
  - For activate env write on you terminal `source env/bin/activate` (*linux) on `venv\Scripts\activate` (Windows)
  - First of all clone this Project
  - Change directory to the project directory `cd sportshop`
  - Checkout to Development branch `git checkout development`
  - Install packages `pip install -r requirements.txt`
  - copy sample.env file `copy sample.env .env`
  - Replace your database credentials in .env file
  - Run on your terminal `python manage.py migrate`
  - Run on your terminal `python manage.py createsuperuser`
  - Run `python manage.py runserver`

## Helpful commands
  - `python manage.py makemigrations` "for migration"
  - `python manage.py runserver host:port` "for starting dev. server"
  - `python manage.py startapp app_name` "for new app"
  - `python manage.py createsuperuser` "For create superuser"


