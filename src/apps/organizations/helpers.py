from apps.methods.models import Method


def get_methods_for_region3(region3_id):
    return Method.objects.filter(network_owner__region3_id=region3_id).exclude(
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY
    )


def filter_methods_by_legal_structure(qs, legal_structure_id):
    return qs.filter(legal_structures__id=legal_structure_id).distinct()
