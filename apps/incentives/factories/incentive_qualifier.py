import factory
from factory.fuzzy import FuzzyChoice

from ..constants import IncentiveQualifierAmount, IncentiveQualifierName
from ..models import IncentiveQualifier
from .incentive import IncentiveFactory


class IncentiveQualifierFactory(factory.django.DjangoModelFactory):
    """Create instance of IncentiveQualifier model."""

    name = FuzzyChoice(
        IncentiveQualifierName.choices,
        getter=lambda name: name[0],
    )
    amount = FuzzyChoice(
        IncentiveQualifierAmount.choices,
        getter=lambda amount: amount[0],
    )
    incentive = factory.SubFactory(IncentiveFactory)

    class Meta:
        model = IncentiveQualifier
