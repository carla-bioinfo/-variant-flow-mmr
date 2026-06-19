"""
VariantFlow-MMR CLI v3 - ETAPA 5
Integração completa: VCF Parsing + ACMG Analysis
"""

import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
import logging
from datetime import datetime

from vflow.analyzer import VariantAnalyzer, AnalysisReport
from vflow.vcf_parser import VCFParser
from vflow.core.acmg_evidence import ACMGEvidenceCollector
from vflow.core.coverage import CoverageAnalyzer
from vflow.core.pms2_assessment import PMS2Assessor
from vflow.core.audit import AuditTrail

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="vflow",
    help="VariantFlow-MMR: Análise profissional de variantes Lynch/MMR",
    no_args_is_help=True,
)

console = Console()


@app.command()
def version():
    """
    Mostra versão e status do VariantFlow-MMR
    """
    console.print(Panel(
        "[bold cyan]VariantFlow-MMR v0.3.0[/bold cyan]\n"
        "[green]ETAPA 5: VCF Parsing + ACMG Analysis[/green]\n"
        f"[dim]{datetime.now().isoformat()}[/dim]",
        title="[bold]VariantFlow[/bold]",
        expand=False,
    ))


@app.command()
def analyze(
    vcf_file: Path = typer.Argument(
        ..., 
        help="Arquivo VCF para análise",
        exists=True
    ),
    gene: Optional[str] = typer.Option(
        None, 
        help="Filtrar por gene (MLH1, MSH2, MSH6, PMS2, EPCAM)"
    ),
    min_depth: int = typer.Option(
        20, 
        help="Cobertura mínima para incluir variante"
    ),
    min_qual: float = typer.Option(
        20.0, 
        help="Score QUAL mínimo"
    ),
    output: Optional[Path] = typer.Option(
        None, 
        help="Salvar relatório em arquivo JSON ou TXT"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", "-v",
        help="Modo verbose com logs detalhados"
    ),
):
    """
    Analisa variantes em arquivo VCF com classificação ACMG.
    
    Exemplo:
        vflow analyze sample.vcf --gene MLH1 --min-depth 30
    """
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    # Header
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]VariantFlow-MMR: Variant Analysis Pipeline[/bold cyan]")
    console.print("=" * 70 + "\n")
    
    console.print(f"[cyan]Input VCF:[/cyan] {vcf_file}")
    console.print(f"[cyan]Min Depth:[/cyan] {min_depth}x")
    console.print(f"[cyan]Min QUAL:[/cyan] {min_qual}")
    if gene:
        console.print(f"[cyan]Gene Filter:[/cyan] {gene}")
    console.print()
    
    try:
        # Inicializar analisador
        with console.status("[bold cyan]Initializing analyzer...") as status:
            analyzer = VariantAnalyzer(str(vcf_file))
        
        # Executar análise
        with console.status("[bold cyan]Analyzing variants..."):
            report = analyzer.analyze(min_depth=min_depth, min_qual=min_qual)
        
        # Mostrar resultados
        console.print(report.summary())
        
        # Estatísticas resumidas
        console.print("\n[bold]Summary Statistics:[/bold]")
        stats_table = Table(show_header=False)
        stats_table.add_row("Total Variants Read:", str(report.variants_total))
        stats_table.add_row("Analyzed:", str(report.variants_analyzed))
        stats_table.add_row("Pass Rate:", 
                          f"{100*report.variants_analyzed/max(report.variants_total, 1):.1f}%")
        console.print(stats_table)
        
        # Detalhe por interpretação
        if report.results:
            console.print("\n[bold]Interpretation Distribution:[/bold]")
            interpretations = {}
            for result in report.results:
                key = result.suggested_interpretation.split(" - ")[0]
                interpretations[key] = interpretations.get(key, 0) + 1
            
            interp_table = Table(show_header=False)
            for interp, count in sorted(interpretations.items()):
                interp_table.add_row(f"{interp}:", str(count))
            console.print(interp_table)
        
        # Salvar output se solicitado
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(report.summary())
            
            console.print(f"\n[green]✓ Report saved to: {output_path}[/green]")
        
        console.print("\n[green]✓ Analysis complete![/green]\n")
        
    except FileNotFoundError as e:
        console.print(f"[red]✗ File not found: {e}[/red]")
        raise typer.Exit(code=1)
    
    except ValueError as e:
        console.print(f"[red]✗ Invalid VCF: {e}[/red]")
        raise typer.Exit(code=1)
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def qc(
    vcf_file: Optional[Path] = typer.Argument(
        None, 
        help="Arquivo VCF para QC (opcional)"
    ),
    gene: str = typer.Option(
        "MLH1", 
        help="Gene para QC"
    ),
):
    """
    Análise de Qualidade (QC) para genes MMR.
    
    Verifica cobertura, profundidade e qualidade de variantes.
    """
    
    console.print(f"\n[bold cyan]Quality Control Analysis[/bold cyan]")
    console.print(f"[cyan]Gene:[/cyan] {gene}\n")
    
    # Validar gene
    valid_genes = ["MLH1", "MSH2", "MSH6", "PMS2", "EPCAM"]
    if gene not in valid_genes:
        console.print(f"[red]✗ Invalid gene: {gene}[/red]")
        console.print(f"   Valid genes: {', '.join(valid_genes)}")
        raise typer.Exit(code=1)
    
    try:
        # Se arquivo VCF fornecido, fazer QC real
        if vcf_file:
            with console.status("[bold cyan]Running QC analysis..."):
                parser = VCFParser(str(vcf_file))
                variants = list(parser.parse())
            
            # Estatísticas
            table = Table(title=f"QC Metrics for {gene}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", style="yellow")
            
            # Coverage
            depths = [v.depth for v in variants if v.depth]
            if depths:
                avg_depth = sum(depths) / len(depths)
                min_depth = min(depths)
                max_depth = max(depths)
                
                table.add_row(
                    "Mean Coverage",
                    f"{avg_depth:.1f}x",
                    "[green]✓ PASS[/green]" if avg_depth >= 30 else "[yellow]WARN[/yellow]"
                )
                table.add_row("Min Coverage", f"{min_depth}x", "-")
                table.add_row("Max Coverage", f"{max_depth}x", "-")
            
            # Variant types
            snv_count = sum(1 for v in variants if v.variant_type == "SNV")
            indel_count = sum(1 for v in variants if v.variant_type in ["Insertion", "Deletion"])
            
            table.add_row("SNVs", str(snv_count), "-")
            table.add_row("Indels", str(indel_count), "-")
            
            console.print(table)
        
        else:
            # QC Demo (sem arquivo)
            table = Table(title=f"QC Metrics for {gene}")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Status", style="yellow")
            
            table.add_row("Coverage Médio", "95x", "[green]✓ PASS[/green]")
            table.add_row("Breadth @ 20x", "98.5%", "[green]✓ PASS[/green]")
            table.add_row("Variant Count", "12", "-")
            table.add_row("SNVs", "8", "-")
            table.add_row("Indels", "4", "-")
            table.add_row(f"{gene} Risk", "LOW", "[green]✓ PASS[/green]")
            
            console.print(table)
            console.print("\n[dim][Modo demo - forneça arquivo VCF para QC real][/dim]")
        
        console.print()
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        raise typer.Exit(code=1)



@app.command()
def report(
    vcf_file: Path = typer.Argument(
        ..., 
        help="Arquivo VCF para análise",
        exists=True
    ),
    output: Path = typer.Option(
        Path("relatorio.html"),
        help="Arquivo HTML de saída"
    ),
):
    """Gera relatório HTML com gráficos de variantes."""
    
    console.print("\n[bold cyan]Gerando Relatório HTML[/bold cyan]\n")
    console.print(f"[cyan]Input VCF:[/cyan] {vcf_file}")
    console.print(f"[cyan]Output HTML:[/cyan] {output}\n")
    
    try:
        from vflow.reports.visualizations import VariantVisualizer
        from vflow.reports.html_reporter import HTMLReporter
        import pandas as pd
        
        with console.status("[bold cyan]Lendo VCF..."):
            parser = VCFParser(str(vcf_file))
            variants = list(parser.parse())
        
        data = pd.DataFrame([
            {
                'chrom': v.chrom,
                'pos': v.pos,
                'ref': v.ref,
                'alt': v.alt,
                'qual': v.qual,
                'gene': 'Unknown',
                'variant_type': 'SNV' if len(v.ref) == len(v.alt) else 'Indel',
            }
            for v in variants
        ])
        
        console.print(f"[green]✓ {len(data)} variantes lidas[/green]")
        
        with console.status("[bold cyan]Gerando gráficos..."):
            viz = VariantVisualizer(output_dir=output.parent)
            charts = viz.generate_all_visualizations(data)
        
        console.print(f"[green]✓ Gráficos criados[/green]")
        
        with console.status("[bold cyan]Criando HTML..."):
            reporter = HTMLReporter(output_dir=output.parent)
            html = reporter.render_html(
                title=f"VariantFlow-MMR: {vcf_file.name}",
                variant_data=data,
                chart_paths=charts
            )
            reporter.save_report(html, output.name)
        
        console.print(f"[green]✓ Relatório: {output}[/green]\n")
        
    except Exception as e:
        console.print(f"[red]✗ Erro: {str(e)}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
