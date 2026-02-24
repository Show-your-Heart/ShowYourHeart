from geopy.geocoders import Nominatim

from apps.methods.models import Method


def get_methods_for_region1(region1):
    return Method.objects.filter(region1=region1).exclude(
        unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY
    )


def filter_methods_by_legal_structure(qs, legal_structure_id):
    return (
        qs.filter(legal_structures__id=legal_structure_id)
        .exclude(unit_of_analysis=Method.UnitAnalysis.EXTERNAL_SURVEY)
        .distinct()
    )


def get_coordinates_from_address(address: str):
    geolocator = Nominatim(user_agent="organizations")
    location = geolocator.geocode(address, timeout=10)

    if location:
        return str(location.latitude), str(location.longitude)
