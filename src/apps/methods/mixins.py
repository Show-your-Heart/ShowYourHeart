import uuid
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import get_dynamic_form
from .helpers import (
    get_form_sections,
    get_gender_field_value,
    get_gender_suffix,
    is_gendered,
)
from .models import (
    Campaign,
    Group,
    Indicator,
    IndicatorResult,
    List,
    Method,
    Section,
    Survey,
)


class MethodFillMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # External survey
        if "token" in kwargs:
            method_fill_context = prepare_method_fill_context(
                None,
                kwargs.get("method"),
                kwargs.get("campaign_id"),
                None,
                kwargs.get("token"),
                self.request,
                None,
            )
        # Method
        else:
            method_fill_context = prepare_method_fill_context(
                None,
                kwargs.get("method"),
                kwargs.get("campaign_id"),
                self.request.user,
                None,
                self.request,
                kwargs.get("project_id"),
            )

        context.update(method_fill_context)
        return context

    @transaction.atomic
    def post(self, request, method_id, campaign_id, project_id=None):
        action = request.POST.get("action")
        if "token" in self.kwargs:
            survey, created = Survey.objects.get_or_create(
                method_id=method_id,
                token=self.kwargs["token"],
                campaign_id=campaign_id,
            )
        else:
            survey, created = Survey.objects.get_or_create(
                method_id=method_id,
                user=request.user,
                organization=request.user.profile.organization,
                project_id=project_id,
                campaign_id=campaign_id,
            )

        current_date = timezone.now()
        if created:
            survey.start_date = current_date

        if action == "submit":
            survey.status = Survey.Status.CLOSED
            survey.closed_date = current_date

        survey.modified_date = current_date

        if survey.status == Survey.Status.TECH_VALIDATED:
            survey.validated_date = current_date

        if survey.status == Survey.Status.QUALITY_CHECKED:
            survey.evaluated_date = current_date

        survey.save()

        save_indicator_results(method_id, request, survey)

        return HttpResponseRedirect(reverse_lazy("methods:method_fill_success"))


def prepare_method_fill_context(
    survey_id=None,
    method=None,
    campaign_id=None,
    user=None,
    token=None,
    request=None,
    project_id=None,
):
    # Get the current survey already started
    try:
        if survey_id is not None:
            survey = Survey.objects.get(pk=survey_id)
            method = survey.method
        elif token is not None:  # External survey
            survey = Survey.objects.get(
                token=token,
                campaign__id=campaign_id,
                method=method,
            )
        else:
            survey = Survey.objects.get(
                user=user,
                campaign__id=campaign_id,
                method=method,
                project_id=project_id,
            )

        readonly = survey.status == Survey.Status.CLOSED
        placeholder_dict = get_previous_campaign_answers(
            survey.campaign.id, survey.method.id, survey.user
        )
        form = get_dynamic_form(
            survey.method,
            IndicatorResult.objects.filter(survey=survey),
            readonly,
            placeholder_dict,
        )

    except ObjectDoesNotExist:
        # If there is none, get new survey
        readonly = False
        placeholder_dict = get_previous_campaign_answers(campaign_id, method.id, user)
        form = get_dynamic_form(method, [], False, placeholder_dict)

    sections = get_sections(method, form(data=request.POST or None))

    try:
        indicators = list(Method.objects.get(id=method.id).indicators.all().values())
        for i in indicators:
            i["unit"] = Indicator.Unit(i["unit"]).label if i["unit"] else ""
            # Add options value
            if i["list_options_id"] is not None:
                list_options = List.objects.get(id=i["list_options_id"])
                options = list_options.items.all().values()
                i["options"] = []
                for o in options:
                    i["options"].append({"id": o["id"], "value": o["value"]})
            # Add group data
            if i["group_id"] is not None:
                group = Group.objects.get(id=i["group_id"])
                group_items = group.items.all().values()
                i["group_title"] = group.title
                i["group_items"] = []
                for o in group_items:
                    i["group_items"].append(
                        {"id": o["id"], "title": o["title"], "suffix": o["suffix"]}
                    )
            # Add group_2 data
            if i["group_2_id"] is not None:
                group = Group.objects.get(id=i["group_2_id"])
                group_items = group.items.all().values()
                i["group_2_title"] = group.title
                i["group_2_items"] = []
                for o in group_items:
                    i["group_2_items"].append(
                        {"id": o["id"], "title": o["title"], "suffix": o["suffix"]}
                    )

        indicators_sets = list(
            Method.objects.get(id=method.id).indicators_sets.all().values()
        )

        for indicators_set in indicators_sets:
            indicators_set.update(
                {
                    "indicators_ids": [
                        str(indicator["id"])
                        for indicator in list(
                            Indicator.objects.filter(sets__code=indicators_set["code"])
                            .all()
                            .values()
                        )
                    ]
                }
            )

    except Method.DoesNotExist:
        indicators = list([])

    return {
        "method_name": method.name,
        "campaign_id": campaign_id,
        "readonly": readonly,
        "form": form,
        "sections": sections,
        "sections_data": get_sections_data(method),
        "indicators": indicators,
        "initial_values": get_initial_values(survey) if "survey" in locals() else {},
        "placeholders": placeholder_dict,
        "indicators_sets": indicators_sets,
    }


def save_indicator_results(method_id, request, survey):
    method = Method.objects.get(pk=method_id)

    for indicator in method.indicators.all():
        field_name = f"question_{indicator.id}"
        save_indicator_result(request, survey, indicator, field_name)

    for indicators_set in method.indicators_sets.all():
        for indicator in indicators_set.indicators.all():
            field_base_name = f"question_{indicator.id}"
            for name, _ in request.POST.items():
                if field_base_name in name and len(name.split("_")) >= 3:
                    instance_number = name.split("_")[2]
                    save_indicator_result(
                        request,
                        survey,
                        indicator,
                        field_base_name,
                        instance_number,
                    )
            # Delete removed indicators sets intances
            for indicator_result in IndicatorResult.objects.filter(
                survey=survey, indicator=indicator
            ):
                full_name = (
                    f"question_{indicator.id}_{indicator_result.instance_number}"
                )
                pending_delete = True
                for name, _ in request.POST.items():
                    if full_name == name or f"{full_name}_na" == name:
                        pending_delete = False
                if pending_delete:
                    indicator_result.delete()


def save_indicator_result(request, survey, indicator, field_name, instance_number=0):
    na = (
        None
        if not indicator.mandatory
        else request.POST.get(
            f"{field_name}_{instance_number}_na"
            if int(instance_number) > 0
            else f"{field_name}_na",
            False,
        )
    )

    # Handle gendered indicators
    if indicator.data_type in [
        Indicator.DataType.INTEGERGENDER,
        Indicator.DataType.DECIMALGENDER,
    ]:
        for suffix, gender in {
            "men": IndicatorResult.Gender.MALE,
            "women": IndicatorResult.Gender.FEMALE,
            "non_binary": IndicatorResult.Gender.NON_BINARY,
        }.items():
            name = (
                f"{field_name}_{suffix}_{instance_number}"
                if int(instance_number) > 0
                else f"{field_name}_{suffix}"
            )
            value = request.POST.get(name)
            if value or na:
                IndicatorResult.objects.update_or_create(
                    survey=survey,
                    indicator=indicator,
                    gender=gender,
                    defaults={
                        "value": "" if value is None else value,
                        "not_applicable": na,
                    },
                    instance_number=instance_number,
                )
            else:
                IndicatorResult.objects.filter(
                    survey=survey,
                    indicator=indicator,
                    gender=gender,
                    instance_number=instance_number,
                ).delete()
    # Handle group indicators
    elif indicator.is_group_indicator:
        for group_item in indicator.group.items.all():
            # Handle lists
            if indicator.group_2 is None:
                name = (
                    f"{field_name}_{group_item.suffix}_{instance_number}"
                    if int(instance_number) > 0
                    else f"{field_name}_{group_item.suffix}"
                )
                value = request.POST.get(name)
                if value or na:
                    IndicatorResult.objects.update_or_create(
                        survey=survey,
                        indicator=indicator,
                        group_item=group_item,
                        defaults={
                            "value": "" if value is None else value,
                            "not_applicable": na,
                        },
                        instance_number=instance_number,
                    )
                else:
                    IndicatorResult.objects.filter(
                        survey=survey,
                        indicator=indicator,
                        group_item=group_item,
                        instance_number=instance_number,
                    ).delete()
            # Handle tables
            else:
                for group_2_item in indicator.group_2.items.all():
                    name = (
                        f"{field_name}_{group_item.suffix}_{group_2_item.suffix}_{instance_number}"
                        if int(instance_number) > 0
                        else f"{field_name}_{group_item.suffix}_{group_2_item.suffix}"
                    )
                    value = request.POST.get(name)
                    if value or na:
                        IndicatorResult.objects.update_or_create(
                            survey=survey,
                            indicator=indicator,
                            group_item=group_item,
                            group_2_item=group_2_item,
                            defaults={
                                "value": "" if value is None else value,
                                "not_applicable": na,
                            },
                            instance_number=instance_number,
                        )
                    else:
                        IndicatorResult.objects.filter(
                            survey=survey,
                            indicator=indicator,
                            group_item=group_item,
                            group_2_item=group_2_item,
                            instance_number=instance_number,
                        ).delete()
                # Save group totals
                value = request.POST.get(f"{field_name}_{group_item.suffix}_total")
                IndicatorResult.objects.update_or_create(
                    survey=survey,
                    indicator=indicator,
                    group_item=group_item,
                    group_2_item=None,
                    is_total=True,
                    defaults={
                        "value": "" if value is None else value,
                        "not_applicable": na,
                    },
                    instance_number=instance_number,
                )
        if indicator_is_numeric(indicator.data_type):
            # Save group2 totals
            if indicator.group_2 is not None:
                for group_2_item in indicator.group_2.items.all():
                    name = (
                        f"{field_name}_{group_2_item.suffix}_total_{instance_number}"
                        if int(instance_number) > 0
                        else f"{field_name}_{group_2_item.suffix}_total"
                    )
                    value = request.POST.get(name)
                    IndicatorResult.objects.update_or_create(
                        survey=survey,
                        indicator=indicator,
                        group_item=None,
                        group_2_item=group_2_item,
                        is_total=True,
                        defaults={
                            "value": "" if value is None else value,
                            "not_applicable": na,
                        },
                        instance_number=instance_number,
                    )
            # Save total
            name = (
                f"{field_name}_total_{instance_number}"
                if int(instance_number) > 0
                else f"{field_name}_total"
            )
            value = request.POST.get(name)
            IndicatorResult.objects.update_or_create(
                survey=survey,
                indicator=indicator,
                group_item=None,
                group_2_item=None,
                is_total=True,
                defaults={
                    "value": "" if value is None else value,
                    "not_applicable": na,
                },
                instance_number=instance_number,
            )
    # Handle standard indicators
    else:
        name = (
            f"{field_name}_{instance_number}"
            if int(instance_number) > 0
            else f"{field_name}"
        )
        values = request.POST.getlist(name)
        formatted_values = "|".join(values)
        if formatted_values or na:
            IndicatorResult.objects.update_or_create(
                survey=survey,
                indicator=indicator,
                defaults={"value": formatted_values, "not_applicable": na},
                instance_number=instance_number,
            )
        else:
            IndicatorResult.objects.filter(
                survey=survey, indicator=indicator, instance_number=instance_number
            ).delete()


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))

        return True
    except ValueError:
        return False


def get_previous_campaign_answers(campaign_id, current_method_id, user):
    placeholder_dict = defaultdict(dict)
    # On previews there is no campaign
    if campaign_id:
        current_campaign = Campaign.objects.get(id=campaign_id)
        if current_campaign.previous_campaign:
            # Check if the method was included on the previous campaign
            previous_campaign = Campaign.objects.filter(
                id=current_campaign.previous_campaign.id,
                methods__id__contains=current_method_id,
            ).first()

            if previous_campaign:
                # Check if the user answered the same method on the previous campaign
                previous_survey = Survey.objects.filter(
                    user=user,
                    campaign__id=previous_campaign.id,
                    method__id=current_method_id,
                ).first()

                if previous_survey:
                    indicator_results = IndicatorResult.objects.filter(
                        survey=previous_survey,
                    )

                    for r in indicator_results:
                        code = r.indicator.code
                        if r.gender is not None:
                            placeholder_dict[code][get_gender_suffix(r.gender)] = (
                                r.value
                            )
                        elif r.group_item is not None and r.group_2_item is not None:
                            if r.group_item.suffix not in placeholder_dict[code]:
                                placeholder_dict[code][r.group_item.suffix] = {}
                            placeholder_dict[code][r.group_item.suffix][
                                r.group_2_item.suffix
                            ] = r.value
                        elif r.group_item is not None and r.group_2_item is None:
                            placeholder_dict[code][r.group_item.suffix] = r.value
                        else:
                            placeholder_dict[code] = r.value

    return placeholder_dict


def get_initial_values(survey):
    indicator_results = IndicatorResult.objects.filter(
        survey=survey,
    ).all()
    initial_values = {}
    for i in indicator_results:
        instance_id = (
            f"{i.indicator.id}_{i.instance_number}"
            if i.instance_number > 0
            else str(i.indicator.id)
        )
        if i.is_total:
            continue
        if is_gendered(i.indicator.data_type):
            initial_values[instance_id] = {
                "value": {
                    "non_binary": get_gender_field_value(
                        indicator_results, i.indicator, "non_binary"
                    ),
                    "male": get_gender_field_value(
                        indicator_results, i.indicator, "male"
                    ),
                    "female": get_gender_field_value(
                        indicator_results, i.indicator, "female"
                    ),
                },
                "not_applicable": i.not_applicable,
                "instance_number": -1 if i.instance_number == 0 else i.instance_number,
            }
        elif i.indicator.is_group_indicator:
            if i.indicator.group_2 is None:
                if instance_id not in initial_values:
                    initial_values[instance_id] = {
                        "value": {},
                        "not_applicable": i.not_applicable,
                        "instance_number": -1
                        if i.instance_number == 0
                        else i.instance_number,
                    }
                    initial_values[instance_id]["value"][i.group_item.suffix] = i.value
                else:
                    initial_values[instance_id]["value"][i.group_item.suffix] = i.value
            else:
                if instance_id not in initial_values:
                    initial_values[instance_id] = {
                        "value": {},
                        "not_applicable": i.not_applicable,
                        "instance_number": -1
                        if i.instance_number == 0
                        else i.instance_number,
                    }
                    for item in i.indicator.group.items.all():
                        initial_values[instance_id]["value"][item.suffix] = {}
                    initial_values[instance_id]["value"][i.group_item.suffix][
                        i.group_2_item.suffix
                    ] = i.value
                else:
                    initial_values[instance_id]["value"][i.group_item.suffix][
                        i.group_2_item.suffix
                    ] = i.value
        else:
            initial_values[instance_id] = {
                "value": i.value,
                "not_applicable": i.not_applicable,
                "instance_number": -1 if i.instance_number == 0 else i.instance_number,
            }

    return initial_values


def get_sections(current_method, form_instance):
    # Convert field objects array into a dictionary
    field_lookup = {name: form_instance[name] for name in form_instance.fields}
    sections = get_form_sections(current_method)
    # Store fields HTML in indicator object
    for _, section in sections.items():
        # Top‑level indicators
        for indicator in section["indicators"]:
            field_obj = field_lookup[indicator["field_name"]]
            indicator["field"] = field_obj

        # Top‑level indicators_sets
        for i_set_dict in section["indicators_sets"]:
            for indicator in i_set_dict["indicators_set"]["indicators"]:
                field_obj = field_lookup[indicator["field_name"]]
                indicator["field"] = field_obj

        for _, subsection_items in section["subsections"].items():
            # Subsection indicators
            for indicator in subsection_items["indicators"]:
                field_obj = field_lookup[indicator["field_name"]]
                indicator["field"] = field_obj

            # Subsection indicators_sets
            for i_set_dict in subsection_items["indicators_sets"]:
                for indicator in i_set_dict["indicators_set"]["indicators"]:
                    field_obj = field_lookup[indicator["field_name"]]
                    indicator["field"] = field_obj

    return sections


def get_sections_data(method):
    sections = Section.objects.filter(method=method).order_by("order")
    sections_data = []
    for section in sections:
        indicators_ids = [i["id"] for i in list(section.indicators.all().values())]
        indicators_sets_ids = [
            s["id"] for s in list(section.indicators_sets.all().values())
        ]

        sections_data.append(
            {
                "id": section.id,
                "title": section.title,
                "description": section.description,
                "indicators_ids": indicators_ids,
                "indicators_sets_ids": indicators_sets_ids,
                "parent_id": section.parent_id,
            }
        )

    return sections_data


def indicator_is_numeric(data_type):
    return (
        data_type == Indicator.DataType.INTEGER
        or data_type == Indicator.DataType.DECIMAL
    )
