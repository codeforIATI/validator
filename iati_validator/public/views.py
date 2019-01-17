"""Public section, including homepage and signup."""
from os.path import join

from flask import Blueprint, render_template, request, redirect, \
    url_for, current_app
import iatikit

from ..extensions import db
from .models import SuppliedData


blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route('/')
def home():
    """Home page."""
    return render_template('public/home.html')


@blueprint.route('/upload/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        form_data = request.form
    else:
        form_data = request.args
    source_url = form_data.get('source_url')
    original_file = request.files.get('original_file')
    raw_text = form_data.get('paste')
    form_name = None

    if source_url:
        form_name = 'url_form'
    elif raw_text:
        form_name = 'text_form'
    elif original_file:
        form_name = 'upload_form'

    supplied_data = SuppliedData(source_url, original_file,
                                 raw_text, form_name)
    db.session.add(supplied_data)
    db.session.commit()
    return redirect(url_for('public.validate', uuid=supplied_data.id))


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


@blueprint.route('/validate/<uuid:uuid>')
def validate(uuid):
    supplied_data = SuppliedData.query.get_or_404(str(uuid))
    filepath = join(current_app.config['MEDIA_FOLDER'],
                    supplied_data.original_file)
    dataset = iatikit.Dataset(filepath)
    return render_template('public/validate.html', data=supplied_data,
                           dataset=dataset)
