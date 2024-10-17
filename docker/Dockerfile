FROM python:3.12-slim as python-base

# ensures that the python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1 \
  # install a handler for SIGSEGV, SIGFPE, SIGABRT, SIGBUS and SIGILL signals
  # to dump the Python traceback
  PYTHONFAULTHANDLER=1 \
  # a random value is used to seed the hashes of str and bytes objects
  PYTHONHASHSEED=random \
  # pip
  # change for CI test
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry. NOTE: remember to update it also on the CI
  POETRY_VERSION=1.8.3 \
  # make poetry install to this location
  POETRY_HOME="/opt/poetry" \
  # make poetry create the virtual environment in the project's root
  # it gets named `.venv`
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  # do not ask any interactive question
  POETRY_NO_INTERACTION=1 \
  # paths
  # this is where our requirements + virtual environment will live
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


###############################################################################
# `builder-base` stage is used to build deps + create our virtual environment
###############################################################################
FROM python-base as builder-base

# 1. -e causes a script to exit if any of the processes it calls generate a
#    non-zero return code
# 2. -o pipefail  makes a pipe chain of scripts return a non-zero code
#    if *any* of the inbetween scripts returned a non-zero code.
SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

# System deps
# hadolint ignore=DL3008
RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends -y \
  curl \
  # Install `poetry` package manager - respects $POETRY_VERSION & $POETRY_HOME:
  # https://github.com/python-poetry/poetry
  && curl -sSL https://install.python-poetry.org | python - \
  && poetry --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove curl \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
# hadolint ignore=DL3008
RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends git \
  && poetry install --only main --no-root --no-ansi \
  && apt-get purge -y --auto-remove git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

###############################################################################
# `development` image is used during development / testing
###############################################################################
FROM builder-base as development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install --no-root

RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends -y \
  gettext \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# will become mountpoint of our code
WORKDIR /srv
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]

###############################################################################
# `production` image used for runtime
###############################################################################
FROM builder-base as production

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY src /srv
WORKDIR /srv
RUN ["python", "manage.py", "collectstatic", "--clear", "--no-input"]
