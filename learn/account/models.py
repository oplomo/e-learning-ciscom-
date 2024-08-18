# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-/]+$",
                _(
                    "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
                ),
                "invalid",
            )
        ],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
