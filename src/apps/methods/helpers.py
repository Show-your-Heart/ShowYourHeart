import re

from .models import IndicatorResult, Invitation, Method


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


def get_external_survey_filter(network_owner__id):
    return Method.objects.filter(
        network_owner__id=network_owner__id,
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY,
    )


def get_survey_stats(survey, method):
    stats = {
        "totalProgress": 0,
        "totalCompleted": 0,
        "totalInProgress": 0,
        "totalToDo": 0,
        "survey": survey,
        "method": method,
        "sectionsWithStatus": [],
    }

    if survey:
        indicator_results = IndicatorResult.objects.filter(
            survey=survey,
        )
        total_indicators = 0
        total_answered__indicators = 0

        for section in method["sections"]:
            total_indicators += section.indicators.count()
            total_section_indicators = section.indicators.count()

            answered_indicators = 0

            for i in section.indicators.all():
                # Get indicator result
                indicator_result = next(
                    (ii for ii in indicator_results if i.id == ii.indicator.id), None
                )
                if indicator_result and indicator_result.value:
                    answered_indicators += 1

            total_answered__indicators += answered_indicators

            if total_section_indicators == answered_indicators:
                stats["totalCompleted"] += 1
                stats["sectionsWithStatus"].append(
                    {"status": "completed", "section": section}
                )
            elif answered_indicators > 0:
                stats["totalInProgress"] += 1
                stats["sectionsWithStatus"].append(
                    {"status": "inProgress", "section": section}
                )
            else:
                stats["totalToDo"] += 1
                stats["sectionsWithStatus"].append(
                    {"status": "toDo", "section": section}
                )

        stats["totalProgress"] = round(
            total_answered__indicators * 100 / total_indicators
        )

    else:
        stats["totalToDo"] = len(method["sections"])
        for section in method["sections"]:
            stats["sectionsWithStatus"].append({"status": "toDo", "section": section})

    return stats
