"""
Testes para a CLI VariantFlow-MMR
"""

from typer.testing import CliRunner
from vflow.cli.main import app

runner = CliRunner()


def test_version_command():
    """Testa comando version"""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "VariantFlow-MMR" in result.stdout
    assert "0.2.0" in result.stdout


def test_qc_command():
    """Testa comando qc"""
    result = runner.invoke(app, ["qc", "--gene", "PMS2"])
    assert result.exit_code == 0
    assert "Quality Control" in result.stdout
    assert "PMS2" in result.stdout


def test_analyze_help():
    """Testa ajuda do comando analyze"""
    result = runner.invoke(app, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "VCF_FILE" in result.stdout
    assert "--gene" in result.stdout


def test_main_help():
    """Testa ajuda geral"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "version" in result.stdout
    assert "analyze" in result.stdout
    assert "qc" in result.stdout
