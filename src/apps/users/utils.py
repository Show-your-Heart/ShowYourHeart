import random


def email_verification_code_regeneration(user_instance):
    """
    Generates a new email verification code randomly for the user
    and stores it in the database.
    """
    new_code = str(random.randint(0000, 9999)).zfill(4)
    user_instance.email_verification_code = new_code
    user_instance.save()
    return new_code
