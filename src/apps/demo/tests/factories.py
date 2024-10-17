from factory.django import DjangoModelFactory

from apps.demo.models import Data


class DataFactory(DjangoModelFactory):
    class Meta:
        model = Data
