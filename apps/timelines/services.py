import csv
from dataclasses import dataclass

from apps.timelines.models import Timeline
from apps.users.models import User


@dataclass
class TimelineCsvData:
    """Represent timeline csv data."""

    category: str
    heading: str
    assigned_to: str
    description: str


def get_data_from_csv_file(file_path: str) -> list[TimelineCsvData]:
    """Return raw data from csv file."""
    with open(file_path, encoding="utf-8") as file:
        data = csv.DictReader(file, delimiter=",")
        return [
            TimelineCsvData(
                category=row["Category"],
                heading=row["Heading"],
                assigned_to=row["Assigned To"],
                description=row["Description"],
            ) for row in data
        ]


def get_timelines_from_csv_data(
    data: list[TimelineCsvData],
    chamber_id: int,
    category_map: dict,
    type_id: int,
    chamber_admin_id: User,
) -> list[Timeline]:
    """Return list of timelines read/imported from csv raw data."""
    return [
        Timeline(
            category_id=category_map.get(row.category),
            name=row.heading,
            assigned_to=row.assigned_to,
            description=row.description,
            chamber_id=chamber_id,
            created_by_id=chamber_admin_id,
            type_id=type_id,
            order=index,
        ) for index, row in enumerate(data)
    ]
