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
