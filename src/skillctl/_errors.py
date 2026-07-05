"""Structured error reporting for build and audit."""

from __future__ import annotations

import json

from rich.console import Console


class Reporter:
    def __init__(self):
        self.errors: list[dict] = []
        self.warnings: list[dict] = []
        self.skipped_count = 0
        
    def skipped(self, path: str, message: str, suggested_fix: str | None = None):
        self.skipped_count += 1
        self.warnings.append({
            "path": path,
            "category": "skipped",
            "message": message,
            "suggested_fix": suggested_fix,
        })
        
    def warning(self, path: str, category: str, message: str, line: int | None = None, suggested_fix: str | None = None):
        self.warnings.append({
            "path": path,
            "line": line,
            "category": category,
            "message": message,
            "suggested_fix": suggested_fix,
        })
        
    def error(self, path: str, category: str, message: str, line: int | None = None, suggested_fix: str | None = None):
        self.errors.append({
            "path": path,
            "line": line,
            "category": category,
            "message": message,
            "suggested_fix": suggested_fix,
        })
        
    def has_errors(self) -> bool:
        return len(self.errors) > 0
        
    def print(self, use_json: bool = False):
        if use_json:
            print(json.dumps({"errors": self.errors, "warnings": self.warnings}, indent=2))
            return
            
        console = Console()
        for w in self.warnings:
            loc = str(w['path'])
            if w.get('line'):
                loc += f":{w['line']}"
            console.print(f"{loc}: {w['message']}")
            if w.get('suggested_fix'):
                console.print(f"  {w['suggested_fix']}")
                
        for e in self.errors:
            loc = str(e['path'])
            if e.get('line'):
                loc += f":{e['line']}"
            console.print(f"{loc}: {e['message']}")
            if e.get('suggested_fix'):
                console.print(f"  {e['suggested_fix']}")
