# ShowYourHeart
Show your Heart application

## Table of contents
* [General info](#general-information)
* [Technologies](#technologies)
* [External services and resources](#external-services-and-resources)

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

### Why this stack?

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

- To send **transactional emails**. It comes with a package to use the [Sendgrid](https://sendgrid.com/en-us) API, and it can use any other provider by using Django's SMTP backend, or adding other libraries to use other provider's APIs.
- To store media files. It comes with the necessary libraries to use **any S3 provider**.
- Access a **PostgreSQL** database.
- Storing the **Docker images**.
- A **remote logging** platform.
- A VPS or serverless service to run the **Docker container**.

