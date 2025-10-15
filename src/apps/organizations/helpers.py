from apps.methods.models import Method


def get_organization_method_filter(legal_structure_id):
    return Method.objects.filter(
        legal_structures__id=legal_structure_id, active=True
    ).exclude(unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY)
