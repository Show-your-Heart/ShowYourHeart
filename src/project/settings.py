"""
Settings for the Django project.

For more information on Django's settings, visit:
    https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import logging
from pathlib import Path

import environ
import structlog
from django.core.management.utils import get_random_secret_key
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

################################################################################
#                               General                                        #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#debug
DEBUG = env("DEBUG", default=False)

# https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key
SECRET_KEY = env.str("SECRET_KEY", default=get_random_secret_key())

# https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Instance's absolute URL (given we're not using Sites framework)
ABSOLUTE_URL = env.str("ABSOLUTE_URL", default="")

# https://github.com/fabiocaccamo/django-maintenance-mode#settings
MAINTENANCE_MODE = env.bool("MAINTENANCE_MODE", default=False)
MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.DefaultStorageBackend"

# https://docs.djangoproject.com/en/4.2/ref/settings/#root-urlconf
ROOT_URLCONF = "project.urls"

# https://docs.djangoproject.com/en/4.2/ref/settings/#wsgi-application
WSGI_APPLICATION = "ptoject.wsgi.application"


################################################################################
#                Internationalization and localization                         #
################################################################################

# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Andorra"

# https://docs.djangoproject.com/en/4.2/ref/settings/#language-code
LANGUAGE_CODE = "en-GB"

# https://docs.djangoproject.com/en/4.2/ref/settings/#languages
LANGUAGES = [
    ("en", _("English")),
    ("ca", _("Catalan")),
]

# https://docs.djangoproject.com/en/4.2/ref/settings/#use-i18n
USE_I18N = True

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-USE_TZ
USE_TZ = True

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-LOCALE_PATHS
LOCALE_PATHS = [str(BASE_DIR / "locale")]

################################################################################
#                               Databases                                      #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default=""),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=5432),
    }
}


################################################################################
#                                  Apps                                        #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#installed-apps
INSTALLED_APPS = [
    "maintenance_mode",
    "django.contrib.postgres",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "flowbite_classes",
    "post_office",
    "django_extensions",
    "active_link",
    "extra_settings",
    "apps.users",
    "project",
    "apps.demo",
]


################################################################################
#                               Middleware                                     #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
    "apps.users.middleware.VerificationRequiredMiddleware",
]


################################################################################
#                                Static                                        #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "static")

# https://docs.djangoproject.com/en/4.2/ref/settings/#static-url
STATIC_URL = "/static/"

# https://docs.djangoproject.com/en/4.2/ref/settings/#staticfiles-dirs
STATICFILES_DIRS = [
    str(BASE_DIR / "assets"),
]

################################################################################
#                             Authentication                                   #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"

# https://docs.djangoproject.com/en/4.2/ref/settings/#login-url
LOGIN_URL = reverse_lazy("registration:login")

# https://docs.djangoproject.com/en/4.2/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = reverse_lazy("home")

# https://docs.djangoproject.com/en/4.2/ref/settings/#logout-redirect-url
LOGOUT_REDIRECT_URL = "/"

# In theory, everywhere that the user will have access while not logged in
# should be also accessible if it's logged in but without the email validated.
VERIFICATION_REQUIRED_IGNORE_VIEW_NAMES = [
    "home",
    "registration:signup",
    "registration:privacy_policy",
    "registration:login",
    "registration:password_reset",
    "registration:password_reset_confirm",
    "registration:password_reset_done",
    "registration:password_reset_complete",
    "registration:password_change",
    "registration:password_change_done",
    "registration:profile_details",
    "registration:logout",
    "registration:profile_details_success",
    "registration:user_validation",
    "registration:send_verification_code",
    "registration:email_verification_complete",
]

################################################################################
#                               Passwords                                      #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


################################################################################
#                               Templates                                      #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#templates
develop_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
production_loaders = [
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "templates",
        ],
        "OPTIONS": {
            "context_processors": [
                "maintenance_mode.context_processors.maintenance_mode",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": develop_loaders if DEBUG else production_loaders,
        },
    },
]
FORM_RENDERER = "flowbite_classes.renderers.CustomFormRenderer"
CODI_COOP_ENABLE_MONKEY_PATCH = True


################################################################################
#                               Media / Storage                                #
################################################################################

# https://docs.djangoproject.com/en/4.2/ref/settings/#media-root
MEDIA_ROOT = env.str("MEDIA_ROOT", default="")

# https://docs.djangoproject.com/en/4.2/ref/settings/#media-url
MEDIA_URL = env.str("MEDIA_URL", default="")

# Wasabi cloud storage configuration
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="")
AWS_DEFAULT_ACL = env.str("AWS_DEFAULT_ACL", default="public-read")
AWS_PUBLIC_MEDIA_LOCATION = env.str(
    "AWS_PUBLIC_MEDIA_LOCATION",
    default="media/public",
)
AWS_PRIVATE_MEDIA_LOCATION = env.str(
    "AWS_PRIVATE_MEDIA_LOCATION",
    default="media/private",
)
AWS_S3_BASE_DOMAIN = env.str("AWS_S3_BASE_DOMAIN", default="")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_BASE_DOMAIN}/{AWS_STORAGE_BUCKET_NAME}"
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "static"

STORAGES = {
    "default": {
        "BACKEND": "project.storage_backends.PublicMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

################################################################################
#                                  Email                                       #
################################################################################

# Post Office
# https://github.com/ui/django-post_office#settings
POST_OFFICE = {
    "BACKENDS": {
        "default": env(
            "POST_OFFICE_DEFAULT_BACKEND",
            default="django.core.mail.backends.console.EmailBackend",
        ),
    },
    "DEFAULT_PRIORITY": env("POST_OFFICE_DEFAULT_PRIORITY", default="now"),
    "MESSAGE_ID_ENABLED": True,
    "MESSAGE_ID_FQDN": env("POST_OFFICE_MESSAGE_ID_FQDN", default="example.com"),
    "CELERY_ENABLED": env("POST_OFFICE_CELERY_ENABLED", bool, default=False),
}

# https://docs.djangoproject.com/en/4.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=None)

# Sendgrid
# https://github.com/sklarsa/django-sendgrid-v5#other-settings
SENDGRID_API_KEY = env("SENDGRID_API_KEY", default="")
SENDGRID_SANDBOX_MODE_IN_DEBUG = env(
    "SENDGRID_SANDBOX_MODE_IN_DEBUG", bool, default=False
)

# SMTP
# These are set to false as default given that Sendgrid's Web API is the default
# https://docs.djangoproject.com/en/4.2/ref/settings/#email
EMAIL_HOST = env.str("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default="")
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

################################################################################
#                         django-extra-settings                                #
################################################################################

PROJECT_NAME = env.str("PROJECT_NAME", default="")
EXTRA_SETTINGS_DEFAULTS = [
    {
        "name": "PROJECT_NAME",
        "type": "Setting.TYPE_STRING",
        "value": PROJECT_NAME,
        "description": _(
            "This name will be used for the HTML title of the "
            "public app, logo alt text and other places."
        ),
    },
    {
        "name": "LOGO",
        "type": "Setting.TYPE_FILE",
        "value": "",
        "description": _(
            "Logo image that will be used to customize the "
            "public app, e-mail templates and other."
        ),
    },
]
EXTRA_SETTINGS_IMAGE_UPLOAD_TO = "django-extra-settings-images"
EXTRA_SETTINGS_FILE_UPLOAD_TO = "django-extra-settings-files"
EXTRA_SETTINGS_VERBOSE_NAME = _("Dynamic settings")

################################################################################
#                                  Logging                                     #
################################################################################

# https://docs.djangoproject.com/en/4.1/ref/logging/
DJANGO_LOG_LEVEL = env.str("DJANGO_LOG_LEVEL", default="WARNING").upper()
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "format": "{name} {levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
    },
    "loggers": {
        # "django_structlog": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        # },
        # Make sure to replace the following logger's name for yours
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer(),
        # structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


################################################################################
#                                  Selenium                                    #
################################################################################

APP_HOST_NAME = env.str("APP_HOST_NAME", default="")
SELENIUM_HOST_NAME = env.str("SELENIUM_HOST_NAME", default="")

################################################################################
#                                  django-active-link                          #
################################################################################

# Needs to be included in tailwind.config.js, in the safelist block.
# Changing the tailwind config requires a Docker image rebuild, and potentially
# to run again the npx compiler as stated in the README.
ACTIVE_LINK_CSS_CLASS = "bg-primary-400"
ACTIVE_LINK_STRICT = True

################################################################################
#                            User groups and permissions                       #
################################################################################

# User group names that are used programmatically in some place, so we don't
# want them hardcoded.
# Beware that these CANNOT BE CHANGED once the instance is already deployed, or
# you are going to end up with a new group with the new name while all the users
# are still assigned to the previous group.
# For the same reason, names cannot be multilingual.
GROUPS = {
    "admins": {
        "name": "Administrators",
        "description": _(
            "Access to: configuration and customization "
            "settings, the log of emails sent by the system, email "
            "templates. Gives permission to edit the fields 'Is staff', "
            "'Is active' and 'Groups'."
        ),
    },
    "manage_users": {
        "name": "User management",
        "description": _(
            "Grants access to adding, viewing, changing and deleting users."
        ),
    },
    "access_logentry": {
        "name": "Access full log entry",
        "description": _(
            "Grants access to the registry of all "
            "actions made by any user within the admin panel."
        ),
    },
}

################################################################################
#                    Initial superuser and dev data                            #
################################################################################

# Credentials for the initial superuser. Leave empty to skip its creation.
# Variables for non-interactive superuser creation
DJANGO_SUPERUSER_EMAIL = env.str("DJANGO_SUPERUSER_EMAIL", default="")
DJANGO_SUPERUSER_PASSWORD = env.str("DJANGO_SUPERUSER_PASSWORD", default="")
USER_ADMIN_EMAIL = env.str("USER_ADMIN_EMAIL", default="")
USER_ADMIN_PASSWORD = env.str("USER_ADMIN_PASSWORD", default="")

################################################################################
#                           Logger / logging                                   #
################################################################################

# Calling this once here sets it for the entire project
logging.basicConfig(level=logging.INFO)
