#!/usr/bin/env python3
"""CLI interface for PM Agentic AI Platform."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agent import run_agent
from src.processors import DocumentParser
from src.generators import FeatureSpecGenerator, UIProposalGenerator, TaskBreakdownGenerator
from src.utils.config import config
from src.utils.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """PM Agentic AI Platform - Product management with AI agents."""
    log_level = "DEBUG" if debug else config.log_level
    setup_logging(level=log_level)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def upload(file_path):
    """Upload a customer interview document (PDF or DOCX)."""
    try:
        file_path = Path(file_path)

        console.print(f"[cyan]Uploading {file_path.name}...[/cyan]")

        # Parse document
        doc_data = DocumentParser.parse(file_path)

        if "error" in doc_data:
            console.print(f"[red]Error: {doc_data['error']}[/red]")
            return

        # Copy to uploads directory
        dest_path = config.upload_dir / file_path.name
        import shutil
        shutil.copy(file_path, dest_path)

        console.print(f"[green]✓ Uploaded successfully to {dest_path}[/green]")
        console.print(f"File type: {doc_data['file_type']}")

        if 'num_pages' in doc_data:
            console.print(f"Pages: {doc_data['num_pages']}")

    except Exception as e:
        console.print(f"[red]Error uploading file: {e}[/red]")
        logger.error(f"Upload error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--files', '-f', multiple=True, help='Interview files to include')
def ask(query, files):
    """Ask a strategic product question."""
    try:
        console.print(Panel.fit(
            f"[bold cyan]Query:[/bold cyan] {query}",
            title="PM Agent",
            border_style="cyan"
        ))

        # Resolve file paths
        file_paths = []
        if files:
            for f in files:
                path = Path(f)
                if not path.exists():
                    # Try in uploads directory
                    path = config.upload_dir / f
                if path.exists():
                    file_paths.append(str(path))
                else:
                    console.print(f"[yellow]Warning: File not found: {f}[/yellow]")

        # Run agent
        console.print("[cyan]Running analysis...[/cyan]")
        result = run_agent(query, file_paths)

        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        # Display results
        display_results(result)

    except Exception as e:
        console.print(f"[red]Error running query: {e}[/red]")
        logger.error(f"Query error: {e}")
        sys.exit(1)


@cli.command()
def analyze():
    """Analyze all uploaded data."""
    try:
        # Find all uploaded files
        files = list(config.upload_dir.glob("*.*"))
        if not files:
            console.print("[yellow]No uploaded files found. Upload interviews first with 'upload' command.[/yellow]")
            return

        console.print(f"[cyan]Analyzing {len(files)} uploaded files...[/cyan]")

        # Run agent
        result = run_agent(
            "What should we build next based on all available data?",
            [str(f) for f in files]
        )

        display_results(result)

    except Exception as e:
        console.print(f"[red]Error analyzing data: {e}[/red]")
        logger.error(f"Analysis error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--port', default=8000, help='Port to run server on')
def serve(port):
    """Start the web UI server."""
    import uvicorn
    console.print(f"[cyan]Starting web server on http://localhost:{port}[/cyan]")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)


def display_results(result: dict):
    """Display agent results in a nice format."""

    # Top feature
    top_feature = result.get("top_feature")
    if top_feature:
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]{top_feature.get('name', 'Feature')}[/bold green]\n\n"
            f"{top_feature.get('description', 'N/A')}\n\n"
            f"[yellow]Confidence:[/yellow] {top_feature.get('confidence', 'unknown')}\n"
            f"[yellow]RICE Score:[/yellow] {top_feature.get('rice_score', 'N/A')}",
            title="🎯 Top Recommendation",
            border_style="green"
        ))

    # Feature spec
    spec = result.get("feature_spec")
    if spec:
        spec_gen = FeatureSpecGenerator()
        spec_md = spec_gen.format_spec_markdown(spec)
        console.print("\n[bold]Feature Specification:[/bold]")
        console.print(Markdown(spec_md))

    # UI proposals
    ui_proposals = result.get("ui_proposals")
    if ui_proposals:
        ui_gen = UIProposalGenerator()
        ui_md = ui_gen.format_proposals_markdown(ui_proposals)
        console.print("\n[bold]UI Proposals:[/bold]")
        console.print(Markdown(ui_md))

    # Task breakdown
    tasks = result.get("task_breakdown")
    if tasks:
        task_gen = TaskBreakdownGenerator()
        tasks_md = task_gen.format_tasks_markdown(tasks)
        console.print("\n[bold]Development Tasks:[/bold]")
        console.print(Markdown(tasks_md))

    # All opportunities
    opportunities = result.get("scored_features", [])
    if opportunities and len(opportunities) > 1:
        console.print(f"\n[bold]Other Opportunities ({len(opportunities) - 1}):[/bold]")
        for i, opp in enumerate(opportunities[1:6], 2):  # Show top 5
            console.print(f"{i}. {opp.get('name')} (Score: {opp.get('rice_score', 'N/A')})")


if __name__ == "__main__":
    cli()
