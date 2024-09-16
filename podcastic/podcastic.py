"""
Main entry point for the Podcastic CLI application.

This module sets up the Typer application and registers all available commands.
"""

import typer
from podcastic.commands import generate, compile, research, write

app = typer.Typer()

app.command(name="generate")(generate.run)
app.command(name="compile")(compile.run)
app.command(name="research")(research.run)
app.command(name="write")(write.run)

if __name__ == "__main__":
    app()