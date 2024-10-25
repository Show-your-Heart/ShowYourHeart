# ShowYourHeart
Show your Heart application

## Table of contents
* [General info](#general-information)
* [Technologies](#technologies)
* [External services and resources](#external-services-and-resources)
* [Local environment setup for development](#local-environment-setup-for-development)
* [Internationalization and localization](#internationalization-and-localization)

## General information

TO DO: include general description of the project's scope.

## Technologies

### Backend

- [Python](https://www.python.org/) 3.12
- [Django](https://www.djangoproject.com/) 5.1

Many other technologies are used in the form of Python packages. Check out
the list in `project.toml`.

### Frontend

- [TailwindCSS](https://tailwindcss.com/)
- [FlowBite](https://github.com/themesberg/flowbite) (a controls and components library for Tailwind)
- [AlpineJS](https://alpinejs.dev/)
- [HTMX](https://htmx.org/)

### Containerization and other tools

- Docker
- npm, for Tailwind compilation
- Poetry, a python package manager

### Why did we choose this stack?

This project (which is a rewrite of a previous version made in Java) was originally
developed by a group of cooperatives and other entities, raising the need of
combining different skill sets and different ways of working. It also aims to be
an easy to contribute and maintain open source project.

Given the expertise of the contributing cooperatives, two possible paradigms
were considered:

1. A SPA with [Vue](https://vuejs.org/) and [Nuxt](https://nuxt.com/), consuming
JSON API provided by [Django Rest Framework](https://www.django-rest-framework.org/).
2. A plain HTML front-end rendered by the Django templates engine, with HTMX and
AlpineJS for advanced interactivity.

We opted for the option 2, meaning that by default each interaction comes
with a full page reload. In places where we considered that a more advanced
ajax or client-side interaction is valuable, we used HTMX and/or AlpineJS.

Some of the reasons to go with the paradigm 2 are:

- Reduce the work load and complexity of the front-end development.
- Simplify the deployment steps and local environment setup.
- Allows us to kick-start the development by using this [django boilerplate](https://github.com/codicoop/boilerplate_django).
- We consider that this stack makes it easier to make changes in the future
if other companies take over the maintenance and for any new contributors.
- Not using a heavy front-end JS framework removes the need for the front-end to
handle routing, state, internationalization, duplication of logic, extra tests,
higher-level framework and packages maintenance, build processes, etc.

There are several different frameworks and technologies to develop custom web
applications to choose from. These are the reasons for our particular selection.

- **Django**: is widely used and robust, with a big community and ecosystem of
packages.
- **HTMX**: in the context of the Django scene, it's the third most popular framework
after React and jQuery. Check out the *"What JavaScript framework(s) do you
use?"* section in [this survey](https://lp.jetbrains.com/django-developer-survey-2023/#technologies-and-frameworks).
- **TailwindCSS**: is very popular (check out the *"What CSS framework(s) do you use?"*
section of the aforementioned survey). It removes the need to define a
CSS structure and naming decisions (which typically is complex and
difficult to understand and maintain in the long term), instead, each HTML
element contains all the information about how it's displayed.
- **AlpineJS**: Is lightweight, increasingly popular, and lets you define
interactions directly in the HTML elements. At the same time it seamlessly
integrates with vanilla JS blocks if you need to. It's a great complement to
HTMX because you can let HTMX handle the requests to the backend and AlpineJS
handle the client-side behaviour.

HTMX, TailwindCSS and AlpineJS all three have in common that the code goes into
the HTML elements' properties, simplifying the development and maintenance and
allowing for a good implementation of the
[Locality of Behaviour](https://htmx.org/essays/locality-of-behaviour/) principle.

Nowadays, there's a constant stream of videos and articles sharing experiences
and analysis of the HTMX stack. For now, we consider [this one](https://htmx.org/essays/a-real-world-react-to-htmx-port/)
to be the best resource to understand it in a real life case.

## External services and resources

The application needs are:

- To send **transactional emails**. It comes with a package to use the [Sendgrid](https://sendgrid.com/en-us)
API, and it can use any other provider by using Django's SMTP backend, or adding
other libraries to use other provider's APIs.
- To store media files. It comes with the necessary libraries to use **any S3 provider**.
- Access a **PostgreSQL** database.
- Storing the **Docker images**.
- A **remote logging** platform.
- A VPS or serverless service to run the **Docker container**.

## Local environment setup for development

### Overview

In your local environment the app will run in a Docker container, along with
a Postgres and a Selenium container.

The app's container mounts the `/src` folder, therefore every change done in
the files inside `/src` will also be applied in the container's code, then
Gunicorn will detect the change and automatically reload the app.

Given this setup, you could already work by cloning the repository, starting the
containers, and just editing the code inside `/src`.

The problem with that is that it will be more difficult to browse around the code,
for example, your IDE will not be able to find the source of the
imported modules.

We recommend you to set it up in a way that you have a local virtual environment
which will allow your IDE to correctly check references, jump to code definitions,
etc, and that's the reason the next steps require you to install a couple of
tools in your system.

### Backend

If you don't intend to make any changes to the Tailwind classes or any css, you
could setup only the backend part.

1. Clone the repository into a local folder.
1. Install Python 3.12, we recommend [pyenv.py](https://github.com/pyenv/pyenv)
for it, by doing `pyenv install 3.12` and then in the repository folder
`pyenv local 3.12`. Finally, check the version by going to the local folder and running `python -V`.
1. Install [Poetry](https://python-poetry.org/) or update it (`poetry self update`) to the latest version.
1. At the project's root, run `poetry install`.
1. Copy the `docker/.env.example` file to `docker/.env` and modify as needed, but
the initial setup should let the project initialize already.
1. Install or update [Docker](https://www.docker.com/) and from the `docker/` folder run `docker compose up --build`.
1. In another terminal, access the docker's container bash (`docker exec -it showyourheart-app bash`) and run `python manage.py migrate`.
1. Open `http://localhost:1601`.

In the future, when you pull a new version of the app, repeat the last 3 steps
to make sure that you create an updated version of the Docker image and database
migrations are applied.

### Frontend

Tailwind needs to "compile" the css files by scanning the templates and
creating a compact css that includes only the Tailwind classes used in the
project.

If you intend to change any Tailwind classes from the html files, you need to
access container's bash and run these commands:

1. `docker exec -it showyourheart-app bash`
1. `cd /front`
1. `npx tailwindcss -i /srv/assets/styles/input.css -o /srv/assets/styles/output.css --watch`

This will start a process that will recompile the css each time you make changes
to any tailwind classes in the templates.

**Important**: if you modify the `package.json`, `package-lock.json` or
`tailwind.config.js` files, you must rebuild the docker image. One way to do it is
by running `docker compose up --build` in the `/docker` directory.

## Internationalization and localization

### Coding good practices

- Make use of [comments for translators](https://docs.djangoproject.com/en/5.1/topics/i18n/translation/#comments-for-translators)
to help clarify the intent of the string.
- Make sure to use placeholders when needed. I.e.: `_("Hi %s, what's up?") % name`.
- All string literals in python files or html templates must be written in english.

### Translations

We use the core Django translations system, so the process of generating the
translations files and the reference for the functions and template tags must
be checked there.

For convenience, we configured the Docker image so it can create the translations
files, given that it some systems you might need to install some additional
library.

Run this command in the docker container:

    python manage.py makemessages --all

Tips:

- When editing a .po file, start by checking that all new strings are in english.
It could happen that by mistake a developer leaves a string in some other language.
In that case, first translate this strings to english directly in the source
code and then generate the .po files again.
- Beware of the strings that look like URL paths: they are URL paths and their
translations must follow the same format (lowercase, without spaces and no special
characters other than dashes).
