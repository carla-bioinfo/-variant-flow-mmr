"""
Unit tests for Audit Trail Module
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from src.vflow.core.audit import AuditTrail, AuditEntry, SystemInfo, GitInfo


class TestAuditEntry:
    """Test individual audit entries"""
    
    def test_audit_entry_creation(self):
        """Test creating an audit entry"""
        entry = AuditEntry(
            id="audit_001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            module="TestModule",
            method="test_method",
            user="testuser",
            version="0.1.0",
            git_commit="abc123def456",
            git_branch="main",
            git_clean=True,
            input_params={"gene": "PMS2"},
            input_hash="sha256:abc123",
            output_hash="sha256:def456",
            duration_seconds=0.123,
            status="SUCCESS"
        )
        
        assert entry.id == "audit_001"
        assert entry.module == "TestModule"
        assert entry.status == "SUCCESS"
    
    def test_audit_entry_to_json(self):
        """Test converting entry to JSON"""
        entry = AuditEntry(
            id="audit_001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            module="TestModule",
            method="test_method",
            user="testuser",
            version="0.1.0",
            git_commit="abc123",
            git_branch="main",
            git_clean=True,
            input_params={"test": "data"},
            input_hash="sha256:abc",
            output_hash="sha256:def",
            duration_seconds=0.5,
            status="SUCCESS"
        )
        
        json_str = entry.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["id"] == "audit_001"
        assert parsed["module"] == "TestModule"
        assert parsed["duration_seconds"] == 0.5


class TestAuditTrail:
    """Test AuditTrail functionality"""
    
    def setup_method(self):
        """Initialize audit trail with temp directory"""
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())
        self.audit = AuditTrail(audit_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up temp directory"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audit_trail_initialization(self):
        """Test initialization of audit trail"""
        assert self.audit.audit_dir == self.temp_dir
        assert self.temp_dir.exists()
    
    def test_record_successful_execution(self):
        """Test recording successful execution"""
        entry = self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"gene": "PMS2", "position": 100},
            output={"result": "success"},
            duration_seconds=0.234,
            status="SUCCESS"
        )
        
        assert entry.id == "audit_001"
        assert entry.status == "SUCCESS"
        assert entry.module == "TestModule"
        assert entry.duration_seconds == 0.234
    
    def test_record_execution_with_warnings(self):
        """Test recording execution with warnings"""
        warnings = ["Warning 1", "Warning 2"]
        entry = self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"test": "data"},
            output={"result": "completed"},
            duration_seconds=0.1,
            status="SUCCESS",
            warnings=warnings
        )
        
        assert entry.warnings == warnings
        assert len(entry.warnings) == 2
    
    def test_record_execution_with_error(self):
        """Test recording execution with error"""
        error_msg = "Test error message"
        entry = self.audit.record_execution(
            module="FailModule",
            method="failing_method",
            input_params={"test": "data"},
            output=None,
            duration_seconds=0.05,
            status="ERROR",
            error_message=error_msg
        )
        
        assert entry.status == "ERROR"
        assert entry.error_message == error_msg
    
    def test_multiple_entries_get_unique_ids(self):
        """Test that multiple entries get unique IDs"""
        entry1 = self.audit.record_execution(
            module="TestModule",
            method="method1",
            input_params={"test": "1"},
            output={"result": "1"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        entry2 = self.audit.record_execution(
            module="TestModule",
            method="method2",
            input_params={"test": "2"},
            output={"result": "2"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        assert entry1.id == "audit_001"
        assert entry2.id == "audit_002"
        assert entry1.id != entry2.id
    
    def test_audit_entry_saved_to_file(self):
        """Test that audit entries are saved to JSON files"""
        self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"gene": "PMS2"},
            output={"result": "success"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        # Check that file was created
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        audit_file = self.temp_dir / today / "audit_001.json"
        
        assert audit_file.exists()
    
    def test_input_hash_calculated(self):
        """Test that input hash is calculated"""
        entry = self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"gene": "PMS2", "position": 100},
            output={"result": "success"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        assert entry.input_hash.startswith("sha256:")
        assert len(entry.input_hash) > 10
    
    def test_output_hash_calculated(self):
        """Test that output hash is calculated"""
        entry = self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"test": "data"},
            output={"result": "success", "criteria": 5},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        assert entry.output_hash.startswith("sha256:")
        assert len(entry.output_hash) > 10
    
    def test_different_inputs_produce_different_hashes(self):
        """Test that different inputs produce different hashes"""
        entry1 = self.audit.record_execution(
            module="TestModule",
            method="test1",
            input_params={"gene": "PMS2"},
            output={"result": "1"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        entry2 = self.audit.record_execution(
            module="TestModule",
            method="test2",
            input_params={"gene": "MLH1"},
            output={"result": "1"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        assert entry1.input_hash != entry2.input_hash
    
    def test_audit_summary(self):
        """Test audit summary generation"""
        self.audit.record_execution(
            module="TestModule",
            method="test_method",
            input_params={"test": "data"},
            output={"result": "success"},
            duration_seconds=0.1,
            status="SUCCESS"
        )
        
        summary = self.audit.get_audit_summary()
        
        assert summary["total_entries"] >= 1
        assert summary["version"] is not None
        assert "audit_dir" in summary
    
    def test_list_audit_logs(self):
        """Test listing audit logs"""
        # Create multiple entries
        for i in range(3):
            self.audit.record_execution(
                module="TestModule",
                method=f"test_{i}",
                input_params={"test": i},
                output={"result": i},
                duration_seconds=0.1,
                status="SUCCESS"
            )
        
        logs = self.audit.list_audit_logs(days=1)
        
        # Should have at least 3 entries
        assert len(logs) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
