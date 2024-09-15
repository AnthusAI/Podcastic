"""
Main entry point for the Podcastic CLI application.

This module sets up the Typer application and registers the generate and compile commands.
"""

import typer
from commands import generate, compile

app = typer.Typer()

app.command(name="generate")(generate.run)
app.command(name="compile")(compile.run)

if __name__ == "__main__":
    app()