#!/usr/bin/env python3

# files2db - A tool to normalize and combine flat files into a database
# Copyright (C) 2024 Louis Le Nezet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Created on 22/10/2021
@author: LouisLeNezet
Script to launch the application
"""

import logging
import os
import sys

import click
import typer
from typer.main import get_command

from files2db.__version__ import __version__
from files2db.main import main

logging.basicConfig(level=logging.INFO)

app = typer.Typer(add_completion=False)

def show_notice():
    typer.echo(f"files2db v{__version__}  Copyright (C) 2024 Louis Le Nezet")
    typer.echo("This program comes with ABSOLUTELY NO WARRANTY; for details type '--warranty'.")
    typer.echo("This is free software, and you are welcome to redistribute it")
    typer.echo("under certain conditions; type '--license' for details.\n")

@app.command()
def cli(
    path: str = typer.Argument(
        None, help="Path to the main file to use."
    ),
    normalize: bool = typer.Option(
        False, "--normalize", "-n", help="Normalize the data after concatenation."
    ),
    output: str = typer.Option(
        "./DataGenerated", "--output", "-o", help="Output directory for the generated files."
    ),
    prefix: str = typer.Option(
        "AllID", "--prefix", "-p", help="Prefix for the output files."
    ),
    license: bool = typer.Option(
        False, "--license", help="Show license information and exit."
    ),
    warranty: bool = typer.Option(
        False, "--warranty", help="Show warranty disclaimer and exit."
    ),
    version: bool = typer.Option(
        False, "--version", help="Show version and exit."
    ),
):
    if version:
        typer.echo(f"files2db version {__version__}")
        raise typer.Exit()

    if license:
        typer.echo(
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.\n\n"
            "See <https://www.gnu.org/licenses/> for details."
        )
        raise typer.Exit()

    if warranty:
        typer.echo(
            "This program is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n\n"
            "See <https://www.gnu.org/licenses/> for details."
        )
        raise typer.Exit()

    # Now path is required if neither license nor warranty is requested
    if path is None:
        typer.echo("Error: Missing argument 'PATH'. Use --help for more info.\n")
        raise typer.Exit(code=1)

    show_notice()

    # Call the main logic
    main(path=path, normalize=normalize, output=output, prefix=prefix)

# Fix for sys.path if needed (optional)
if sys.path[0] in ("", os.getcwd()):
    sys.path.pop(0)

if __package__ == "":
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Get the click.Command object from Typer
        command = get_command(app)
        ctx = click.Context(command)
        typer.echo(command.get_help(ctx))
        sys.exit(0)
    app()
