from apps.methods.models import Method


def get_methods_for_region1(region1):
    return Method.objects.filter(region1=region1).exclude(
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY
    )


def filter_methods_by_legal_structure(qs, legal_structure_id):
    return qs.filter(legal_structures__id=legal_structure_id).distinct()
