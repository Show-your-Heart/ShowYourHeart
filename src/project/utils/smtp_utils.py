def get_smtp_for_user(user, network):
    """
    Return the SMTPServer for a specific network.
    Must explicitly pass a network, since user can have more than one.
    """
    if not network:
        raise ValueError("You must provide a network to send emails.")
    return getattr(network, "smtp_server", None)
