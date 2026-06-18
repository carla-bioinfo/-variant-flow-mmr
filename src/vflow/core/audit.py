"""
Audit Trail Module for VariantFlow-MMR

Implements comprehensive logging and traceability for all analyses.
Ensures compliance with clinical laboratory standards (CAP, CLIA, ISO 15189).

Purpose:
- Record WHEN analysis was performed (timestamp)
- Record WHO performed it (user)
- Record WHAT version was used (git commit, version)
- Record DATA INTEGRITY (hashes)
- Enable reproducibility (git allows exact reconstruction)

This is NOT encryption or security.
This IS transparency and reproducibility.
"""

import os
import json
import hashlib
import socket
import subprocess
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SystemInfo:
    """Information about the system where analysis ran"""
    user: str
    hostname: str
    python_version: str
    platform: str


@dataclass
class GitInfo:
    """Information about git commit and repository state"""
    commit_hash: str
    branch: str
    is_clean: bool
    author: str


@dataclass
class AuditEntry:
    """
    A single audit trail entry.
    
    Records everything about ONE execution of ONE method.
    """
    id: str                                    # "audit_001", "audit_002", etc
    timestamp: str                             # ISO 8601 format
    module: str                                # "ACMGEvidenceCollector"
    method: str                                # "collect_evidence"
    user: str                                  # from os.getenv('USER')
    version: str                               # from __version__
    git_commit: str                            # git commit hash
    git_branch: str                            # git branch name
    git_clean: bool                            # was repo clean?
    
    input_params: Dict[str, Any]              # what parameters were passed?
    input_hash: str                            # SHA256 of inputs
    output_hash: str                           # SHA256 of output
    
    duration_seconds: float                    # how long did it take?
    status: str                                # "SUCCESS", "ERROR", "WARNING"
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self), indent=2)
    
    def save(self, filepath: Path) -> None:
        """Save audit entry to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
        logger.info(f"Audit entry saved to {filepath}")


class AuditTrail:
    """
    Record and manage audit trails for all analyses.
    
    This ensures:
    - Compliance with laboratory standards
    - Reproducibility of results
    - Traceability of who did what when
    - Data integrity (hashes)
    """
    
    # Default audit log directory
    DEFAULT_AUDIT_DIR = Path.home() / "variant-flow-mmr" / "audit_logs"
    
    def __init__(self, audit_dir: Optional[Path] = None):
        """
        Initialize AuditTrail.
        
        Args:
            audit_dir: Directory to save audit logs. Defaults to DEFAULT_AUDIT_DIR
        """
        self.audit_dir = audit_dir or self.DEFAULT_AUDIT_DIR
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Load version
        try:
            from src.vflow.__version__ import __version__
            self.version = __version__
        except ImportError:
            self.version = "unknown"
        
        # Collect system info once
        self.system_info = self._get_system_info()
        self.git_info = self._get_git_info()
        
        logger.info(f"AuditTrail initialized. Logs at: {self.audit_dir}")
    
    def record_execution(
        self,
        module: str,
        method: str,
        input_params: Dict[str, Any],
        output: Any,
        duration_seconds: float,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None
    ) -> AuditEntry:
        """
        Record execution of a method.
        
        Args:
            module: Name of module (e.g., "ACMGEvidenceCollector")
            method: Name of method (e.g., "collect_evidence")
            input_params: Dictionary of input parameters
            output: The result/output object
            duration_seconds: How long the method took
            status: "SUCCESS", "ERROR", or "WARNING"
            error_message: If status is ERROR, the error message
            warnings: List of warnings encountered
            
        Returns:
            AuditEntry that was recorded
        """
        
        # Calculate hashes
        input_hash = self._calculate_hash(input_params)
        output_hash = self._calculate_hash(output)
        
        # Generate ID
        timestamp = datetime.now(timezone.utc).isoformat()
        entry_id = self._generate_entry_id()
        
        # Create audit entry
        audit_entry = AuditEntry(
            id=entry_id,
            timestamp=timestamp,
            module=module,
            method=method,
            user=self.system_info.user,
            version=self.version,
            git_commit=self.git_info.commit_hash,
            git_branch=self.git_info.branch,
            git_clean=self.git_info.is_clean,
            input_params=input_params,
            input_hash=input_hash,
            output_hash=output_hash,
            duration_seconds=duration_seconds,
            status=status,
            error_message=error_message,
            warnings=warnings or []
        )
        
        # Save to file
        self._save_audit_entry(audit_entry)
        
        # Log
        logger.info(
            f"Execution recorded: {module}.{method} "
            f"({status}, {duration_seconds:.3f}s, commit {self.git_info.commit_hash[:7]})"
        )
        
        return audit_entry
    
    def _get_system_info(self) -> SystemInfo:
        """Collect system information"""
        import sys
        import platform
        
        return SystemInfo(
            user=os.getenv('USER', 'unknown'),
            hostname=socket.gethostname(),
            python_version=sys.version.split()[0],
            platform=platform.system()
        )
    
    def _get_git_info(self) -> GitInfo:
        """Collect git information"""
        try:
            # Get commit hash
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=Path.home() / "variant-flow-mmr",
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception as e:
            logger.warning(f"Could not get git commit: {e}")
            commit = "unknown"
        
        try:
            # Get branch name
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=Path.home() / "variant-flow-mmr",
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception:
            branch = "unknown"
        
        try:
            # Check if repo is clean
            status = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                cwd=Path.home() / "variant-flow-mmr",
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            is_clean = len(status) == 0
        except Exception:
            is_clean = False
        
        try:
            # Get author (from git config)
            author = subprocess.check_output(
                ['git', 'config', 'user.name'],
                cwd=Path.home() / "variant-flow-mmr",
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
        except Exception:
            author = "unknown"
        
        return GitInfo(
            commit_hash=commit,
            branch=branch,
            is_clean=is_clean,
            author=author
        )
    
    def _calculate_hash(self, data: Any) -> str:
        """
        Calculate SHA256 hash of data.
        
        Used to verify data integrity (detect alterations).
        """
        try:
            # Convert to JSON string for consistent hashing
            if hasattr(data, '__dict__'):
                data_str = json.dumps(asdict(data), sort_keys=True, default=str)
            elif isinstance(data, dict):
                data_str = json.dumps(data, sort_keys=True, default=str)
            else:
                data_str = json.dumps(str(data), default=str)
            
            # Calculate SHA256
            hash_obj = hashlib.sha256(data_str.encode('utf-8'))
            return f"sha256:{hash_obj.hexdigest()}"
        except Exception as e:
            logger.warning(f"Could not calculate hash: {e}")
            return "sha256:error"
    
    def _generate_entry_id(self) -> str:
        """Generate unique audit entry ID"""
        # Count existing entries in today's directory
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_dir = self.audit_dir / today
        today_dir.mkdir(exist_ok=True)
        
        # Count JSON files
        existing = list(today_dir.glob("audit_*.json"))
        next_num = len(existing) + 1
        
        return f"audit_{next_num:03d}"
    
    def _save_audit_entry(self, entry: AuditEntry) -> None:
        """Save audit entry to file"""
        # Organize by date
        date_str = entry.timestamp.split('T')[0]
        date_dir = self.audit_dir / date_str
        date_dir.mkdir(exist_ok=True)
        
        # Save with entry ID as filename
        filepath = date_dir / f"{entry.id}.json"
        entry.save(filepath)
    
    def list_audit_logs(self, days: int = 7) -> List[str]:
        """List recent audit logs"""
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        audit_files = []
        for json_file in self.audit_dir.rglob("*.json"):
            mtime = datetime.fromtimestamp(json_file.stat().st_mtime, tz=timezone.utc)
            if mtime >= cutoff_date:
                audit_files.append(str(json_file))
        
        return sorted(audit_files, reverse=True)
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of audit activities"""
        audit_files = self.list_audit_logs(days=1)
        
        summary = {
            "total_entries": len(audit_files),
            "audit_dir": str(self.audit_dir),
            "version": self.version,
            "git_commit": self.git_info.commit_hash,
            "recent_files": audit_files[:5]
        }
        
        return summary


# Example usage (for testing)
if __name__ == "__main__":
    # Initialize audit trail
    audit = AuditTrail()
    
    print("\n" + "="*70)
    print("TEST 1: Recording a successful execution")
    print("="*70)
    
    # Simulate an execution
    entry1 = audit.record_execution(
        module="ACMGEvidenceCollector",
        method="collect_evidence",
        input_params={
            "gene": "PMS2",
            "chromosome": "chr7",
            "position": 6012876,
            "reference": "C",
            "alternate": "T"
        },
        output={"variant": "PMS2:chr7:6012876:C>T", "criteria_found": 3},
        duration_seconds=0.234,
        status="SUCCESS"
    )
    
    print(f"\nAudit Entry Created:")
    print(f"  ID: {entry1.id}")
    print(f"  Timestamp: {entry1.timestamp}")
    print(f"  Module: {entry1.module}.{entry1.method}")
    print(f"  User: {entry1.user}")
    print(f"  Git Commit: {entry1.git_commit[:7]}")
    print(f"  Input Hash: {entry1.input_hash[:20]}...")
    print(f"  Output Hash: {entry1.output_hash[:20]}...")
    print(f"  Duration: {entry1.duration_seconds:.3f}s")
    print(f"  Status: {entry1.status}")
    
    print("\n" + "="*70)
    print("TEST 2: Recording with warnings")
    print("="*70)
    
    entry2 = audit.record_execution(
        module="PMS2Assessor",
        method="assess_variant",
        input_params={"gene": "PMS2", "position": 21000, "variant_type": "SNV"},
        output={"risk_level": "CRITICAL"},
        duration_seconds=0.045,
        status="SUCCESS",
        warnings=["Position in critical region - orthogonal validation recommended"]
    )
    
    print(f"\nAudit Entry with Warning:")
    print(f"  ID: {entry2.id}")
    print(f"  Warnings: {entry2.warnings}")
    
    print("\n" + "="*70)
    print("TEST 3: Audit summary")
    print("="*70)
    
    summary = audit.get_audit_summary()
    print(f"\nAudit Summary:")
    print(f"  Total entries today: {summary['total_entries']}")
    print(f"  Version: {summary['version']}")
    print(f"  Git commit: {summary['git_commit'][:7]}")
    print(f"  Audit directory: {summary['audit_dir']}")
    
    print("\n" + "="*70)
    print("TEST 4: List recent audit logs")
    print("="*70)
    
    recent = audit.list_audit_logs(days=1)
    print(f"\nRecent audit logs: {len(recent)} entries")
    if recent:
        print("Latest 3:")
        for log in recent[:3]:
            print(f"  - {log}")
