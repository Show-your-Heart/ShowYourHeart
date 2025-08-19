import re

from .models import Invitation


class ParseExternalInvitations:
    def parse_csv(self, csv_reader, id):
        error_messages = []
        for row in csv_reader:
            if row[1]:
                if self.is_valid_email(row[1]):
                    Invitation.objects.update_or_create(
                        email=row[1],
                        external_survey_invitation_id=id,
                        defaults={
                            "name": row[0],
                        },
                    )
                else:
                    error_messages.append(f"The email {row[1]} is not valid")
            else:
                error_messages.append(f"The email for {row[0]} is empty")

        return error_messages

    def is_valid_email(self, email):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        if re.fullmatch(regex, email):
            return True
        else:
            return False
