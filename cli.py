"""
AgentGuard CLI — Command Line Interface
Usage: agentguard [COMMAND] [OPTIONS]
"""

import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from agentguard.analyzer import AgentAnalyzer
from agentguard.parser import AgentArchitectureParser

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="AgentGuard")
def main():
    """
    \b
    ╔═══════════════════════════════════════╗
    ║  🛡️  AgentGuard v0.1.0                ║
    ║  Agentic AI Threat Modeling Framework ║
    ╚═══════════════════════════════════════╝

    Analyze, score, and report on security threats in agentic AI systems.
    """
    pass


# ─────────────────────────────────────────
# COMMAND: analyze
# ─────────────────────────────────────────
@main.command()
@click.option(
    "--input", "-i",
    required=True,
    type=click.Path(exists=True),
    help="Path to agent architecture YAML/JSON file"
)
@click.option(
    "--output", "-o",
    default="agentguard_report.html",
    help="Output report file path (default: agentguard_report.html)"
)
@click.option(
    "--format", "-f",
    "output_format",
    default="html",
    type=click.Choice(["html", "md", "pdf"], case_sensitive=False),
    help="Report output format (default: html)"
)
@click.option(
    "--fail-on",
    default=None,
    help="Exit with code 1 if threats at these levels exist. E.g. --fail-on critical,high"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed scoring breakdown"
)
def analyze(input, output, output_format, fail_on, verbose):
    """Analyze an agent architecture and generate a threat model report."""

    console.print(Panel.fit(
        "[bold blue]AgentGuard Threat Analysis[/bold blue]\n"
        f"Input:  {input}\n"
        f"Output: {output} ({output_format.upper()})",
        border_style="blue"
    ))

    with console.status("[bold green]Loading agent architecture..."):
        parser = AgentArchitectureParser(input)
        agent = parser.parse()

    console.print(f"[green]✓[/green] Agent loaded: [bold]{agent.name}[/bold] (v{agent.version})")
    console.print(f"[green]✓[/green] Autonomy Level: {agent.autonomy_level}/5")
    console.print(f"[green]✓[/green] Tools detected: {len(agent.tools)}")
    console.print(f"[green]✓[/green] Memory type: {agent.memory.type}")

    with console.status("[bold green]Running threat analysis..."):
        analyzer = AgentAnalyzer(agent)
        report = analyzer.run(verbose=verbose)

    # Print summary table
    _print_summary_table(report)

    # Export report
    with console.status(f"[bold green]Generating {output_format.upper()} report..."):
        report.export(output, format=output_format)

    console.print(f"\n[bold green]✓ Report saved to:[/bold green] {output}")

    # CI/CD fail-on logic
    if fail_on:
        levels = [l.strip().lower() for l in fail_on.split(",")]
        should_fail = False
        if "critical" in levels and report.count_by_level("critical") > 0:
            should_fail = True
        if "high" in levels and report.count_by_level("high") > 0:
            should_fail = True

        if should_fail:
            console.print(
                f"\n[bold red]❌ FAILED:[/bold red] Threats found at level(s): {fail_on}"
            )
            sys.exit(1)


def _print_summary_table(report):
    """Render a rich summary table to the console."""
    table = Table(title="Threat Model Summary", show_header=True, header_style="bold magenta")
    table.add_column("Level", style="bold", width=12)
    table.add_column("Count", justify="right")
    table.add_column("Top Threat", style="dim")

    levels = [
        ("🔴 Critical", "critical", "red"),
        ("🟠 High", "high", "orange3"),
        ("🟡 Medium", "medium", "yellow"),
        ("🟢 Low", "low", "green"),
    ]

    for label, level, color in levels:
        count = report.count_by_level(level)
        top = report.top_threat_by_level(level)
        top_name = top.name if top else "—"
        table.add_row(
            f"[{color}]{label}[/{color}]",
            str(count),
            top_name
        )

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold]Overall Risk Score:[/bold] {report.overall_score:.1f} / 10.0 "
                  f"({report.overall_level.upper()})\n")


# ─────────────────────────────────────────
# COMMAND: list-threats
# ─────────────────────────────────────────
@main.command("list-threats")
@click.option("--domain", "-d", default=None, help="Filter by threat domain")
@click.option(
    "--severity", "-s",
    default=None,
    type=click.Choice(["critical", "high", "medium", "low"], case_sensitive=False),
    help="Filter by base severity level"
)
def list_threats(domain, severity):
    """List all threats in the AgentGuard taxonomy."""
    from agentguard.taxonomy import ThreatTaxonomy

    taxonomy = ThreatTaxonomy.load()
    threats = taxonomy.get_threats(domain=domain, severity=severity)

    table = Table(
        title=f"AgentGuard Threat Taxonomy ({len(threats)} threats)",
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("ID", width=20)
    table.add_column("Domain", width=22)
    table.add_column("Threat Name", width=40)
    table.add_column("Base Severity", width=14)
    table.add_column("ATLAS Technique", width=16)

    severity_colors = {
        "critical": "red", "high": "orange3",
        "medium": "yellow", "low": "green"
    }

    for threat in threats:
        color = severity_colors.get(threat.base_severity, "white")
        table.add_row(
            threat.id,
            threat.domain,
            threat.name,
            f"[{color}]{threat.base_severity.upper()}[/{color}]",
            threat.atlas_technique or "—"
        )

    console.print(table)


# ─────────────────────────────────────────
# COMMAND: score
# ─────────────────────────────────────────
@main.command()
@click.option("--threat", "-t", required=True, help="Threat ID (e.g. PI-001)")
@click.option(
    "--agent", "-a",
    required=True,
    type=click.Path(exists=True),
    help="Path to agent architecture YAML"
)
def score(threat, agent):
    """Score a specific threat against an agent architecture."""
    from agentguard.scorer import RiskScorer
    from agentguard.taxonomy import ThreatTaxonomy

    parser = AgentArchitectureParser(agent)
    agent_obj = parser.parse()

    taxonomy = ThreatTaxonomy.load()
    threat_obj = taxonomy.get_by_id(threat)

    if not threat_obj:
        console.print(f"[red]Error:[/red] Threat ID '{threat}' not found. "
                      "Run `agentguard list-threats` to see all IDs.")
        sys.exit(1)

    scorer = RiskScorer(agent_obj)
    result = scorer.score_threat(threat_obj)

    console.print(Panel.fit(
        f"[bold]{result.threat.name}[/bold]\n\n"
        f"Threat ID:          {result.threat.id}\n"
        f"Domain:             {result.threat.domain}\n"
        f"ATLAS Technique:    {result.threat.atlas_technique or 'N/A'}\n\n"
        f"[bold]Scoring Breakdown[/bold]\n"
        f"  Exploitability:       {result.exploitability:.2f}\n"
        f"  Impact:               {result.impact:.2f}\n"
        f"  Autonomy Factor:      {result.autonomy_factor:.2f}\n"
        f"  Blast Radius:         {result.blast_radius:.2f}\n"
        f"  Reversibility:        {result.reversibility:.2f}\n"
        f"  Detection Difficulty: {result.detection_difficulty:.2f}\n"
        f"  Mitigations Present:  {result.mitigation_factor:.2f}\n\n"
        f"[bold]Final Risk Score:  {result.final_score:.1f} / 10.0[/bold]\n"
        f"Risk Level:         {result.risk_level.upper()}\n\n"
        f"[bold]Recommendation:[/bold]\n{result.threat.recommendation}",
        title="Threat Score",
        border_style="blue"
    ))


# ─────────────────────────────────────────
# COMMAND: init
# ─────────────────────────────────────────
@main.command()
@click.option("--name", "-n", required=True, help="Agent name")
@click.option(
    "--output", "-o",
    default=None,
    help="Output YAML file path (default: <agent-name>.yaml)"
)
def init(name, output):
    """Generate a blank agent architecture template."""
    from agentguard.templates_engine import generate_agent_template

    output_path = output or f"{name.lower().replace(' ', '_')}.yaml"
    template = generate_agent_template(name)

    with open(output_path, "w") as f:
        f.write(template)

    console.print(f"[green]✓[/green] Agent template created: [bold]{output_path}[/bold]")
    console.print("Edit this file to describe your agent, then run:")
    console.print(f"  [cyan]agentguard analyze --input {output_path}[/cyan]")


# ─────────────────────────────────────────
# COMMAND: validate
# ─────────────────────────────────────────
@main.command()
@click.option(
    "--input", "-i",
    required=True,
    type=click.Path(exists=True),
    help="Agent YAML file to validate"
)
def validate(input):
    """Validate an agent architecture YAML against the AgentGuard schema."""
    from agentguard.parser import AgentArchitectureParser
    from agentguard.schema import validate_agent_schema

    errors = validate_agent_schema(input)
    if not errors:
        console.print(f"[bold green]✓ Valid:[/bold green] {input} passes schema validation.")
    else:
        console.print(f"[bold red]✗ Validation failed:[/bold red] {len(errors)} error(s) found:\n")
        for e in errors:
            console.print(f"  [red]•[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
