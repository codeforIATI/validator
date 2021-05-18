"""User models."""
from datetime import datetime
from enum import Enum
from os import makedirs
from os.path import join
import re
import uuid

import requests
from werkzeug.utils import secure_filename
from flask import current_app

from .helpers import trim
from ..extensions import db


class SuppliedData(db.Model):
    """Supplied data to be validated."""

    class FormName(Enum):
        """Form name helper class."""

        upload_form = 'File upload'
        url_form = 'Downloaded from URL'
        text_form = 'Pasted into textarea'

    id = db.Column(db.String(40), primary_key=True)
    source_url = db.Column(db.String(2000))
    original_file = db.Column(db.String(100))

    downloaded = db.Column(db.Boolean(True))

    form_name = db.Column(db.Enum(FormName))
    validated = db.Column(db.Boolean(False))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def upload_dir(self):
        """Returns the folder that the data was uploaded to."""
        return join(current_app.config['MEDIA_FOLDER'], self.id)

    @property
    def xml_errors(self):
        """Returns a list of XML validation errors."""
        return [x for x in self.validation_errors
                if x.error_type == 'xml_error']

    @property
    def iati_errors(self):
        """Returns a list of IATI schema validation errors."""
        return [x for x in self.validation_errors
                if x.error_type == 'iati_error']

    @property
    def codelist_errors(self):
        """Returns a list of IATI codelist validation errors."""
        return [x for x in self.validation_errors
                if x.error_type == 'codelist_error']

    def __init__(self, source_url, file, raw_text, form_name):
        """Constructs a new supplied data model, and fetches the data."""
        self.id = str(uuid.uuid4())  # pylint: disable=invalid-name

        if form_name == 'url_form':
            self.source_url = source_url

            request_kwargs = {
                'headers': {'User-Agent': 'Code for IATI Validator'},
                'stream': True,
                'verify': False,
            }
            resp = requests.get(source_url, **request_kwargs)
            filename = resp.url.split('/')[-1].split('?')[0][:100]
            if filename == '':
                filename = 'file.xml'
            elif not filename.endswith('.xml'):
                filename += '.xml'
            filename = secure_filename(filename)
            makedirs(self.upload_dir(), exist_ok=True)
            filepath = join(self.upload_dir(), filename)
            with open(filepath, 'wb') as handler:
                for block in resp.iter_content(1024):
                    handler.write(block)
        elif form_name == 'upload_form':
            filename = file.filename
            # save the file
            filename = secure_filename(filename)
            makedirs(self.upload_dir(), exist_ok=True)
            filepath = join(self.upload_dir(), filename)
            file.save(filepath)
        else:
            filename = 'paste.xml'
            makedirs(self.upload_dir(), exist_ok=True)
            filepath = join(self.upload_dir(), filename)
            with open(filepath, 'w') as handler:
                handler.write(raw_text)

        self.original_file = join(self.id, filename)
        self.form_name = form_name
        self.created = datetime.utcnow()


class ValidationError(db.Model):
    """Class for modelling an individual validation error."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods

    id = db.Column(db.String(40), primary_key=True)
    supplied_data_id = db.Column(
        db.String, db.ForeignKey('supplied_data.id'), nullable=False)
    supplied_data = db.relationship(
        'SuppliedData', backref=db.backref('validation_errors', lazy=True))
    error_type = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(1000), nullable=False)
    line = db.Column(db.Integer, nullable=True)
    path = db.Column(db.String(200), nullable=True)
    occurrences = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(200), nullable=True)

    @property
    def can_show(self):
        """Determines if an example of the error can be linked."""
        if not (self.path or self.line):
            return False
        match = re.search(r'/iati-(?:activity|organisation)\[(\d+)\]',
                          self.path)
        return bool(match)

    def __init__(self, error_type, iatikit_error, occurrences, supplied_data):
        """Constructs a validation error."""
        self.id = str(uuid.uuid4())  # pylint: disable=invalid-name
        self.error_type = trim(error_type, 50)
        self.summary = trim(iatikit_error.summary, 200)
        self.details = trim(iatikit_error.details, 1000)
        self.line = iatikit_error.line
        self.path = trim(iatikit_error.path, 200)
        self.url = trim(iatikit_error.url, 200)
        self.occurrences = occurrences
        self.supplied_data = supplied_data
