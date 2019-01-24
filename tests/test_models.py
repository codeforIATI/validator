"""Model unit tests."""
import pytest

from iati_validator.public.models import SuppliedData
from iati_validator.extensions import db


@pytest.mark.usefixtures('db')
def test_get_by_uuid():
    """Get SuppliedData by UUID."""
    supplied_data = SuppliedData(None, None, 'Raw XML', 'text_form')
    db.session.add(supplied_data)
    db.session.commit()

    retrieved = SuppliedData.query.get_or_404(supplied_data.id)
    assert retrieved == supplied_data
