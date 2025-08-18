from .models import Invitation


class ParseExternalInvitations:
    def parse_csv(self, csv_reader, id):
        for row in csv_reader:
            if row[1]:
                Invitation.objects.create(
                    name=row[0], email=row[1], external_survey_invitation_id=id
                )

        return "un mensaje"
