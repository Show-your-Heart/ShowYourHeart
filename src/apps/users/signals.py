from django.apps import apps
from django.conf import settings
from django.db.backends.utils import logger


def update_user_groups(sender, **kwargs):
    """
    The motivation for this signal is: in most cases we need to prevent all the
    users (including admins) from modifying the permission groups. In addition
    to that, we want the developers to be able to set and change permission groups
    to keep them in sync with the changes in the project.
    For those reasons, we:
    - Only the developers will have a superuser account
    - Make sure that any other user can never change the permission groups
    - Supply this signal for the developers to be able to maintain the groups

    This function is triggered on post_migrate signal, that is: after every
    "migrate" command, even if there are no new migrations to apply. This script
     must be designed with this in mind.

    Signals are defined in the App declaration (apps.py)

    To specify permissions using this file you need the codename of each one,
    which sometimes can be tricky to find.
    The function print_existing_permissions() is provided to
    help you see each Permission's codename. It can usually be deduced,
    but it also helps to have a full list of available permissions.
    """

    # Administradors
    permissions = {
        "post_office": get_permission_codenames("email", "v")
        + get_permission_codenames("log", "v")
        + get_permission_codenames("emailtemplate", "v"),
        # post_office also has the 'attachment' model. Not giving access for now.
    }
    create_group(settings.GROUP_ADMINS, permissions)

    # Manage Users
    permissions = {
        "users": get_permission_codenames("user", "vacd")
        + get_permission_codenames("profile", "vacd"),
    }
    create_group(settings.GROUP_MANAGE_USERS, permissions)

    # Access LogEntry (Entrades del registre)
    permissions = {"admin": get_permission_codenames("logentry", "c")}
    create_group(settings.GROUP_ACCESS_LOGENTRY, permissions)

    # Superusers
    """
    This block is to clarify which things are meant to be reserved for superusers.
    That means that no other user group declaration should include these.
    - acotags.activity
    - django auth.groups
    """


def create_group(name, permissions):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    group, created = group_model.objects.get_or_create(
        name=name,
    )
    # Using set(), to entirely replace the permissions of this group by the
    # new ones.
    group.permissions.set(get_permissions(permission_model, permissions))
    group.save()
    if created:
        logger.info(f"Grup {name} creat.")
    else:
        logger.info(f"Grup {name} ja existent, permisos actualitzats.")


def get_permissions(permission_model, permissions_dict: dict):
    """
    This function takes all the permissions codenames and contenttype labels
    from the dictionary and returns a list with the queryset of each Permission
    registry.
    We need that to create the m2m relationship between the Group
    and Permission.
    """
    permissions = []
    for content_type__app_label, codenames in permissions_dict.items():
        permissions += permission_model.objects.filter(
            content_type__app_label=content_type__app_label, codename__in=codenames
        )
    return permissions


def get_permission_codenames(base_codename, permissions):
    """
    :param permissions: String containing any of these letters: avcd
    :return: List with all the combinations for the codename.
    """
    strings = []
    if "a" in permissions:
        strings.append(f"add_{base_codename}")
    if "v" in permissions:
        strings.append(f"view_{base_codename}")
    if "c" in permissions:
        strings.append(f"change_{base_codename}")
    if "d" in permissions:
        strings.append(f"delete_{base_codename}")
    return strings


def check_constance_permissions():
    contenttype_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    content_type = contenttype_model.objects.get(
        app_label="constance",
        model="config",
    )
    logger.info(content_type)
    change_perm = permission_model.objects.filter(
        content_type=content_type,
        codename="change_config",
    )
    view_perm = permission_model.objects.filter(
        content_type=content_type,
        codename="view_config",
    )
    logger.info(f"{change_perm=}, {view_perm=}")


def print_existing_permissions():
    from pprint import pprint

    permission_model = apps.get_model("auth", "Permission")
    for i in permission_model.objects.all():
        pprint(i.__dict__)
