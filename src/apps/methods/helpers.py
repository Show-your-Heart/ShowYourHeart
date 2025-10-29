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
        for section, section_data in method["sections"].items():
            total_indicators += section.indicators.count()
            total_section_indicators = section.indicators.count()
            indicators_list = list(section.indicators.all())
            answered_indicators = 0

            for subsection in section_data["subsections"]:
                for _, subsection_indicators in subsection.items():
                    total_indicators += len(subsection_indicators)
                    total_section_indicators += len(subsection_indicators)
                    indicators_list += subsection_indicators

            for i in indicators_list:
                # Get indicator result
                indicator_result = next(
                    (ii for ii in indicator_results if i.id == ii.indicator.id),
                    None,
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

        if total_indicators == 0:
            stats["totalProgress"] = 100
        else:
            stats["totalProgress"] = round(
                total_answered__indicators * 100 / total_indicators
            )

    else:
        stats["totalToDo"] = len(method["sections"])
        for section in method["sections"]:
            stats["sectionsWithStatus"].append({"status": "toDo", "section": section})

    return stats


def is_gendered(data_type):
    if data_type == "IG":
        return True
    else:
        return False


def get_gender_suffix(gender: IndicatorResult.Gender):
    return {
        IndicatorResult.Gender.MALE: "male",
        IndicatorResult.Gender.FEMALE: "female",
        IndicatorResult.Gender.NON_BINARY: "non_binary",
    }.get(gender)


def get_gender_field_value(indicator_result_list, indicator, suffix):
    field_value = None

    gender_lookup = {
        "male": IndicatorResult.Gender.MALE,
        "female": IndicatorResult.Gender.FEMALE,
        "non_binary": IndicatorResult.Gender.NON_BINARY,
    }
    indicator_result = next(
        (
            res
            for res in indicator_result_list
            if res.indicator == indicator and res.gender == gender_lookup[suffix]
        ),
        None,
    )

    if indicator_result:
        field_value = indicator_result.value

    return field_value


def parse_indicators_from_expression(expr: str):
    tokens = expr.split()
    indicators_project_id = []
    for token in tokens:
        if re.match(r"^[a-zA-Z_]\w*$", token):
            indicators_project_id.append(token)

    return indicators_project_id
