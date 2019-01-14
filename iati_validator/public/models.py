"""User models."""
from datetime import datetime
from enum import Enum
from os import makedirs
from os.path import join
import uuid

import requests
from werkzeug.utils import secure_filename
from flask import current_app

from ..extensions import db


class SuppliedData(db.Model):
    """A user of the app."""
    class FormName(Enum):
        upload_form = 'File upload'
        url_form = 'Downloaded from URL'
        text_form = 'Pasted into textarea'

    id = db.Column(db.String(40), primary_key=True)
    source_url = db.Column(db.String(2000))
    original_file = db.Column(db.String(100))

    downloaded = db.Column(db.Boolean(True))

    form_name = db.Column(db.Enum(FormName))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def generate_uuid(self):
        return str(uuid.uuid4())

    def upload_dir(self):
        return join(current_app.config['MEDIA_FOLDER'], self.id)

    def __init__(self, source_url, file, raw_text, form_name):
        self.id = self.generate_uuid()

        if form_name == 'url_form':
            self.source_url = source_url

            request_kwargs = {
                'headers': {'User-Agent': 'IATI Validator'},
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
            filename = 'test.xml'
            makedirs(self.upload_dir(), exist_ok=True)
            filepath = join(self.upload_dir(), filename)
            with open(filepath, 'w') as f:
                f.write(raw_text)

        self.original_file = join(self.id, filename)
        self.form_name = form_name
        self.created = datetime.utcnow()
