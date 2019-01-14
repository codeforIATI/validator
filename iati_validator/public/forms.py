"""Public forms."""
from flask_wtf import FlaskForm
from flask_wtf.html5 import URLField
from wtforms.validators import url


class UploadForm(FlaskForm):
    """Upload form."""

    url = URLField(validators=[url()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(UploadForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(UploadForm, self).validate()
        if not initial_validation:
            return False

        return True
