"""Public section, including homepage and signup."""
from os.path import join, exists
import re

from flask import Blueprint, render_template, request, redirect, \
    url_for, current_app, send_file, flash
import iatikit
from pygments import highlight
from pygments.lexers.html import XmlLexer
from pygments.formatters import HtmlFormatter

from ..extensions import db
from .models import SuppliedData, ValidationError


blueprint = Blueprint('public', __name__,  # pylint: disable=invalid-name
                      static_folder='../static')


@blueprint.route('/')
def home():
    """Show the home page."""
    return render_template('public/home.html')


@blueprint.route('/upload/', methods=['GET', 'POST'])
def upload():
    """Upload a dataset for validation."""
    if request.method == 'POST':
        form_data = request.form
    else:
        form_data = request.args
    source_url = form_data.get('url')
    original_file = request.files.get('file')
    raw_text = form_data.get('paste')
    form_name = None

    if source_url:
        form_name = 'url_form'
    elif raw_text:
        form_name = 'text_form'
    elif original_file:
        form_name = 'upload_form'
    else:
        flash('Error: No data provided', 'danger')
        return redirect(url_for('public.home'))

    supplied_data = SuppliedData(source_url, original_file,
                                 raw_text, form_name)
    db.session.add(supplied_data)
    db.session.commit()
    return redirect(url_for('public.validate', uuid=supplied_data.id))


@blueprint.route('/badge.svg')
def badge():
    """Show the validation status of a dataset as an SVG badge."""
    source_url = request.args.get('url')
    if source_url is None:
        svg_file = join('static', 'badges', 'no-url.svg')
        return send_file(svg_file, mimetype='image/svg+xml')
    supplied_data = SuppliedData(source_url, None, None, 'url_form')

    filepath = join(current_app.config['MEDIA_FOLDER'],
                    supplied_data.original_file)
    dataset = iatikit.Dataset(filepath)

    if dataset.validate_xml() and dataset.validate_iati() \
            and dataset.validate_codelists():
        svg_file = join('static', 'badges', 'passing.svg')
    else:
        svg_file = join('static', 'badges', 'failing.svg')
    return send_file(svg_file, mimetype='image/svg+xml')


@blueprint.route('/validate/<uuid:uuid>')
def validate(uuid):
    """Show the validation results for a supplied dataset."""
    supplied_data = SuppliedData.query.get_or_404(str(uuid))
    filepath = join(current_app.config['MEDIA_FOLDER'],
                    supplied_data.original_file)
    if not exists(filepath):
        flash('Error: That dataset is no longer available', 'danger')
        return redirect(url_for('public.home'))
    dataset = iatikit.Dataset(filepath)

    if supplied_data.validated:
        errors = {
            'xml_errors': supplied_data.xml_errors,
            'iati_errors': supplied_data.iati_errors,
            'codelist_errors': supplied_data.codelist_errors,
        }
    else:
        errors = {
            'xml_errors': [],
            'iati_errors': [],
            'codelist_errors': [],
        }
        valid_xml = dataset.validate_xml()
        if valid_xml:
            dataset.unminify_xml()
            valid_iati = dataset.validate_iati()
            for error, count in valid_iati.error_summary:
                iati_error = ValidationError(
                    'iati_error', error, count, supplied_data)
                errors['iati_errors'].append(iati_error)
                db.session.add(iati_error)

            valid_codelists = dataset.validate_codelists()
            for error, count in valid_codelists.error_summary:
                codelist_error = ValidationError(
                    'codelist_error', error, count, supplied_data)
                errors['codelist_errors'].append(codelist_error)
                db.session.add(codelist_error)
        else:
            for error, count in valid_xml.error_summary:
                xml_error = ValidationError(
                    'xml_error', error, count, supplied_data)
                errors['xml_errors'].append(xml_error)
                db.session.add(xml_error)

    success = all([e == [] for e in errors.values()])

    supplied_data.validated = True
    db.session.add(supplied_data)
    db.session.commit()

    return render_template('public/validate.html',
                           data=supplied_data, dataset=dataset,
                           errors=errors, success=success)


@blueprint.route('/show/<uuid:uuid>')
def show(uuid):
    """Show a validation error in its XML context."""
    validation_error = ValidationError.query.get_or_404(str(uuid))
    filepath = join(current_app.config['MEDIA_FOLDER'],
                    validation_error.supplied_data.original_file)
    if not exists(filepath):
        flash('That dataset is no longer available', 'danger')
        return redirect(url_for('public.home'))
    match = re.search(r'/iati-(?:activity|organisation)\[(\d+)\]',
                      validation_error.path)
    act_num = int(match.group(1)) - 1
    dataset = iatikit.Dataset(filepath)
    dataset.unminify_xml()
    activity = dataset.activities[act_num]
    start_line = activity.etree.sourceline
    line = validation_error.line - start_line + 1
    highlighted_xml = highlight(activity.xml, XmlLexer(),
                                HtmlFormatter(linenos='inline',
                                              lineanchors='L',
                                              hl_lines=[line],
                                              linenostart=start_line))
    return render_template('public/show_error.html',
                           code=highlighted_xml)
