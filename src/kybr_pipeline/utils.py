from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("America/Belem")


def calculate_refs(ref_ini: str, ref_fin: str) -> list[str]:
    """Calculate the references between ref_ini and ref_fin.

    Args:
        ref_ini: The initial reference in the format 'YYYYMM'.
        ref_fin: The final reference in the format 'YYYYMM'.

    Returns:
        A list of references between ref_ini and ref_fin.
    """
    start_date = datetime.strptime(ref_ini, "%Y%m").replace(tzinfo=TIMEZONE)
    end_date = datetime.strptime(ref_fin, "%Y%m").replace(tzinfo=TIMEZONE)

    if start_date > end_date:
        raise ValueError("ref_ini must be less than or equal to ref_fin.")

    references: list[str] = []
    current_date = start_date

    while current_date <= end_date:
        references.append(current_date.strftime("%Y%m"))
        # Move to the next month
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (current_date.month // 12)
        current_date = current_date.replace(year=next_year, month=next_month)

    return references
