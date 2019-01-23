"""Click commands."""
import os
from glob import glob
from subprocess import call

import click


@click.command()
def lint():
    """Lint and check code style with flake8 and isort."""
    skip = ['node_modules', 'requirements', 'venv', 'migrations']
    root_files = glob('*.py')
    root_directories = [
        name for name in next(os.walk('.'))[1] if not name.startswith('.')]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo('{}: {}'.format(description, ' '.join(command_line)))
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    execute_tool('Checking code style', 'flake8')
