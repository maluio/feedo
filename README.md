# Feedo - Personal Feed Reader

A non-fancy personal feed reader.

![architecture](./docs/screenshot.png)

## Supported Feed Sources

* RSS
* Reddit (using [PRAW](https://praw.readthedocs.io/en/stable/index.html))
* e-mail

## Requirements

* **python3** + **pip3**
* **sqlite3**
* A **Reddit account** with subscriptions of the subreddits you'd like to fetch

## Recommended Architecture

Feedo doesn't require a specific architecture. Any environment that runs a webserver + python3 code should be fine. However, this is one possible way to run it:

![architecture](./docs/feedo-architecture.png)

## Installation for Development

Create a `.env` file in the document root with:

```bash
# change to your local path!
DB_FILE=/path/to/your/db/feedo.db3
APP_ENV=dev
# for pytest
DJANGO_SETTINGS_MODULE=config.settings
```

Run:

```bash
$ pip3 install -r requirements.txt
$ ./manage.py runserver
```

