from django.contrib import admin
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

from project.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, password
        and extra fields.
        """
        if not email:
            raise ValueError(_("Users must have an email address"))

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given email, password
        and extra fields.
        """
        if not password:
            raise ValueError(_("Superusers must have a password"))

        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_("name"), max_length=50)
    surnames = models.CharField(
        _("surname"),
        max_length=50,
        default="",
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("email address"),
        max_length=255,
        unique=True,
    )
    email_verification_code = models.CharField(default="0000")
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name

    @property
    @admin.display(
        ordering="name",
        description=_("name"),
    )
    def full_name(self):
        return f"{self.name} {self.surnames}".strip()

    def has_admin_role(self):
        return self.is_staff or self.is_superuser

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
