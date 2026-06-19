"""
Testes para a CLI VariantFlow-MMR - ETAPA 5
"""

from typer.testing import CliRunner
from pathlib import Path
from vflow.cli.main import app

runner = CliRunner()


class TestVersionCommand:
    """Testes do comando version"""
    
    def test_version_command(self):
        """Testa comando version"""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "VariantFlow-MMR" in result.stdout
        assert "0.3.0" in result.stdout
        assert "ETAPA 5" in result.stdout
    
    def test_version_format(self):
        """Verifica formato do output"""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "VariantFlow" in result.stdout


class TestQCCommand:
    """Testes do comando qc"""
    
    def test_qc_command_demo(self):
        """Testa comando qc sem arquivo (demo)"""
        result = runner.invoke(app, ["qc", "--gene", "PMS2"])
        assert result.exit_code == 0
        assert "Quality Control" in result.stdout
        assert "PMS2" in result.stdout
        assert "PASS" in result.stdout
    
    def test_qc_with_vcf(self):
        """Testa comando qc com arquivo VCF real"""
        vcf_path = Path("examples/sample_lynch.vcf")
        if vcf_path.exists():
            result = runner.invoke(app, ["qc", str(vcf_path)])
            assert result.exit_code == 0
            assert "Mean Coverage" in result.stdout or "Coverage" in result.stdout
    
    def test_qc_invalid_gene(self):
        """Testa qc com gene inválido"""
        result = runner.invoke(app, ["qc", "--gene", "INVALID"])
        assert result.exit_code == 1
        assert "Invalid gene" in result.stdout


class TestAnalyzeCommand:
    """Testes do comando analyze"""
    
    def test_analyze_help(self):
        """Testa ajuda do comando analyze"""
        result = runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "VCF_FILE" in result.stdout
    
    def test_analyze_with_vcf(self):
        """Testa analyze com arquivo VCF real"""
        vcf_path = Path("examples/sample_lynch.vcf")
        if vcf_path.exists():
            result = runner.invoke(app, ["analyze", str(vcf_path)])
            assert result.exit_code == 0
            assert "Analysis Pipeline" in result.stdout or "VariantFlow" in result.stdout
    
    def test_analyze_with_min_depth(self):
        """Testa analyze com filtro min_depth"""
        vcf_path = Path("examples/sample_lynch.vcf")
        if vcf_path.exists():
            result = runner.invoke(
                app, 
                ["analyze", str(vcf_path), "--min-depth", "50"]
            )
            assert result.exit_code == 0
            assert "Total Variants" in result.stdout or "Pass Rate" in result.stdout
    
    def test_analyze_missing_file(self):
        """Testa analyze com arquivo inexistente"""
        result = runner.invoke(app, ["analyze", "nonexistent.vcf"])
        # Typer retorna 2 para erro de validação (exists=True falha)
        assert result.exit_code in [1, 2]
        assert "Error" in result.stdout or "error" in result.stdout.lower()


class TestMainCommand:
    """Testes do comando principal"""
    
    def test_main_help(self):
        """Testa ajuda geral"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "version" in result.stdout
        assert "analyze" in result.stdout
        assert "qc" in result.stdout
    
    def test_main_no_args(self):
        """Testa execução sem argumentos"""
        result = runner.invoke(app, [])
        assert result.exit_code in [0, 2]


class TestIntegration:
    """Testes de integração end-to-end"""
    
    def test_full_pipeline(self):
        """Testa pipeline completo: version + analyze + qc"""
        vcf_path = Path("examples/sample_lynch.vcf")
        
        # Version
        v_result = runner.invoke(app, ["version"])
        assert v_result.exit_code == 0
        assert "0.3.0" in v_result.stdout
        
        # Analyze (se VCF existe)
        if vcf_path.exists():
            a_result = runner.invoke(app, ["analyze", str(vcf_path)])
            assert a_result.exit_code == 0
            
            # QC
            q_result = runner.invoke(app, ["qc", str(vcf_path)])
            assert q_result.exit_code == 0
