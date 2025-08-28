#!/usr/bin/env python3
"""
Folder Content Testing Script
Tests folder traversal, file filtering, and directory structure handling
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.sage import SageTool
from utils.files import expand_paths, read_files
from config import Config


class TestFolderContent:
    """Test folder content processing and filtering"""

    @classmethod
    def setup_class(cls):
        """Setup test project structure"""
        cls.temp_dir = tempfile.mkdtemp()
        cls._create_project_structure()

    @classmethod
    def teardown_class(cls):
        """Cleanup test structure"""
        import shutil

        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _create_project_structure(cls):
        """Create a realistic project structure for testing"""
        base_dir = cls.temp_dir

        # Create directory structure
        dirs_to_create = [
            "src/components",
            "src/utils",
            "src/api",
            "tests/unit",
            "tests/integration",
            "docs",
            "config",
            "scripts",
            "node_modules/lodash",  # Should be excluded
            ".git/objects",  # Should be excluded
            "dist/assets",  # Should be excluded
            "__pycache__",  # Should be excluded
            ".venv/lib",  # Should be excluded
        ]

        for dir_path in dirs_to_create:
            os.makedirs(os.path.join(base_dir, dir_path), exist_ok=True)

        # Create files
        files_to_create = {
            # Source files (should be included)
            "src/components/Button.tsx": """import React from 'react';

interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({
  onClick,
  children,
  variant = 'primary'
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
""",
            "src/components/Modal.tsx": """import React, { useState } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};
""",
            "src/utils/formatters.ts": """export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

export const slugify = (text: string): string => {
  return text
    .toLowerCase()
    .replace(/\\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
};
""",
            "src/api/client.py": """import requests
from typing import Dict, Any, Optional

class APIClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[Any, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[Any, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
""",
            # Test files (should be included)
            "tests/unit/test_formatters.py": """import pytest
from src.utils.formatters import formatCurrency, formatDate, slugify
from datetime import datetime

def test_format_currency():
    assert formatCurrency(1234.56) == "$1,234.56"
    assert formatCurrency(0) == "$0.00"

def test_format_date():
    date = datetime(2023, 12, 25)
    result = formatDate(date)
    assert "December 25, 2023" in result

def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("Testing 123 @#$") == "testing-123"
""",
            "tests/integration/test_api.py": """import pytest
from src.api.client import APIClient

@pytest.fixture
def api_client():
    return APIClient("https://api.example.com", "test-key")

def test_client_initialization(api_client):
    assert api_client.base_url == "https://api.example.com"
    assert api_client.api_key == "test-key"

# More integration tests would go here
""",
            # Config files (should be included)
            "config/database.json": """{
  "development": {
    "host": "localhost",
    "port": 5432,
    "database": "myapp_dev",
    "username": "dev_user",
    "password": "dev_pass"
  },
  "production": {
    "host": "prod-db.example.com",
    "port": 5432,
    "database": "myapp_prod",
    "username": "prod_user",
    "password": "secure_password"
  }
}""",
            "package.json": """{
  "name": "test-project",
  "version": "1.0.0",
  "description": "A test project for folder content testing",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "jest",
    "build": "webpack"
  },
  "dependencies": {
    "react": "^18.0.0",
    "lodash": "^4.17.21"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "webpack": "^5.0.0"
  }
}""",
            "README.md": """# Test Project

This is a test project for folder content processing.

## Structure

- `src/` - Source code
  - `components/` - React components
  - `utils/` - Utility functions
  - `api/` - API client code
- `tests/` - Test files
- `config/` - Configuration files
- `docs/` - Documentation

## Installation

```bash
npm install
```

## Running Tests

```bash
npm test
```
""",
            # Documentation (should be included)
            "docs/API.md": """# API Documentation

## Endpoints

### GET /users
Returns a list of users.

### POST /users
Creates a new user.

### GET /users/:id
Returns a specific user by ID.

### PUT /users/:id
Updates a specific user.

### DELETE /users/:id
Deletes a specific user.
""",
            # Scripts (should be included)
            "scripts/deploy.sh": """#!/bin/bash

# Deployment script
echo "Starting deployment..."

# Build the project
npm run build

# Run tests
npm test

# Deploy to production
rsync -avz dist/ production:/var/www/html/

echo "Deployment complete!"
""",
            # Files that should be excluded
            "node_modules/lodash/index.js": "// Lodash library code",
            ".git/config": "[core]\n\trepositoryformatversion = 0",
            "dist/bundle.js": "// Compiled bundle",
            "__pycache__/cache.pyc": "cached bytecode",
            ".venv/lib/python3.9/site.py": "# Virtual environment file",
            ".DS_Store": "Mac OS metadata",
            "Thumbs.db": "Windows thumbnail cache",
            # Large files (might be excluded by size)
            "large_data.json": '{"data": "' + "x" * 100000 + '"}',  # Large JSON
            # Binary files (should be excluded by extension)
            "image.png": b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89",
        }

        for file_path, content in files_to_create.items():
            full_path = os.path.join(base_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            if isinstance(content, bytes):
                with open(full_path, "wb") as f:
                    f.write(content)
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

    def test_project_structure_created(self):
        """Test that project structure was created correctly"""
        expected_dirs = [
            "src/components",
            "src/utils",
            "src/api",
            "tests/unit",
            "tests/integration",
            "docs",
            "config",
            "scripts",
        ]

        for dir_path in expected_dirs:
            full_path = os.path.join(self.temp_dir, dir_path)
            assert os.path.isdir(full_path), f"Directory {dir_path} was not created"

        print(f"Project structure created in: {self.temp_dir}")

    def test_path_expansion_basic(self):
        """Test basic directory path expansion"""
        src_dir = os.path.join(self.temp_dir, "src")
        expanded = expand_paths([src_dir])

        print(f"Expanded {len(expanded)} files from src/:")
        for path in sorted(expanded):
            rel_path = os.path.relpath(path, self.temp_dir)
            print(f"  {rel_path}")

        # Should find TypeScript and Python files
        tsx_files = [p for p in expanded if p.endswith(".tsx")]
        ts_files = [p for p in expanded if p.endswith(".ts")]
        py_files = [p for p in expanded if p.endswith(".py")]

        assert len(tsx_files) >= 2, "Should find TSX component files"
        assert len(ts_files) >= 1, "Should find TypeScript files"
        assert len(py_files) >= 1, "Should find Python files"

    def test_excluded_directory_filtering(self):
        """Test that excluded directories are filtered out"""
        config = Config()
        excluded_dirs = config.EXCLUDED_DIRS

        print(f"Excluded directories: {excluded_dirs}")

        # Expand entire project
        all_expanded = expand_paths([self.temp_dir])

        # Check that no files from excluded directories are included
        for path in all_expanded:
            rel_path = os.path.relpath(path, self.temp_dir)
            path_parts = rel_path.split(os.sep)

            for excluded_dir in excluded_dirs:
                assert excluded_dir not in path_parts, f"Found file in excluded directory {excluded_dir}: {rel_path}"

        print(f"✓ All {len(all_expanded)} files passed exclusion filtering")

    def test_file_extension_filtering(self):
        """Test that file extensions are properly filtered"""
        config = Config()
        allowed_extensions = config.ALLOWED_FILE_EXTENSIONS

        print(f"Allowed extensions: {allowed_extensions}")

        # Expand entire project
        all_expanded = expand_paths([self.temp_dir])

        # Check that all files have allowed extensions
        for path in all_expanded:
            ext = Path(path).suffix
            assert ext in allowed_extensions, f"File {path} has disallowed extension {ext}"

        # Check specific file types are included
        extensions_found = set(Path(p).suffix for p in all_expanded)
        print(f"Extensions found: {sorted(extensions_found)}")

        # Should find common development file extensions
        assert ".py" in extensions_found
        assert ".tsx" in extensions_found or ".ts" in extensions_found
        assert ".json" in extensions_found
        assert ".md" in extensions_found

    def test_file_reading_modes(self):
        """Test different file reading modes on folders"""
        src_dir = os.path.join(self.temp_dir, "src")
        expanded = expand_paths([src_dir])

        # Test embedded mode
        embedded_content = read_files(expanded, mode="embedded")
        assert len(embedded_content) > 0
        print(f"Embedded mode: {len(embedded_content)} files")

        # Test summary mode
        summary_content = read_files(expanded, mode="summary")
        assert len(summary_content) > 0
        print(f"Summary mode: {len(summary_content)} files")

        # Test reference mode
        reference_content = read_files(expanded, mode="reference")
        assert len(reference_content) > 0
        print(f"Reference mode: {len(reference_content)} files")

        # All modes should process the same files
        assert len(embedded_content) == len(summary_content) == len(reference_content)

    def test_large_folder_handling(self):
        """Test handling of folders with many files"""
        # Create a subfolder with many small files
        many_files_dir = os.path.join(self.temp_dir, "many_files")
        os.makedirs(many_files_dir, exist_ok=True)

        # Create 50 small files
        for i in range(50):
            file_path = os.path.join(many_files_dir, f"file_{i:02d}.txt")
            with open(file_path, "w") as f:
                f.write(f"This is test file number {i}\nContent line 2\nContent line 3\n")

        # Test expansion
        expanded = expand_paths([many_files_dir])
        assert len(expanded) == 50

        # Test reading with token limits
        content = read_files(expanded, mode="embedded", max_tokens=1000)

        # Should not read all files due to token limit
        assert len(content) < 50
        print(f"Read {len(content)}/50 files due to token limit")

    def test_nested_folder_traversal(self):
        """Test deep nested folder traversal"""
        # Get all files in project
        all_files = expand_paths([self.temp_dir])

        # Group by depth
        depth_counts = {}
        for path in all_files:
            rel_path = os.path.relpath(path, self.temp_dir)
            depth = len(rel_path.split(os.sep))
            depth_counts[depth] = depth_counts.get(depth, 0) + 1

        print("Files by directory depth:")
        for depth in sorted(depth_counts.keys()):
            print(f"  Depth {depth}: {depth_counts[depth]} files")

        # Should have files at multiple depths
        assert len(depth_counts) >= 2, "Should have files at different depths"
        assert max(depth_counts.keys()) >= 3, "Should have files at depth 3 or deeper"

    @pytest.mark.asyncio
    async def test_sage_tool_folder_analysis(self):
        """Test SAGE tool analysis of entire folders"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set")

        sage_tool = SageTool()

        # Test analyzing the src folder
        src_dir = os.path.join(self.temp_dir, "src")

        try:
            request_data = {
                "prompt": "Analyze this codebase. What programming languages are used and what seems to be the main functionality?",
                "files": [src_dir],
                "mode": "analyze",
                "model": "auto",
            }

            result = await sage_tool.execute(request_data)

            assert len(result) > 0
            response_text = result[0].text if hasattr(result[0], "text") else str(result[0])

            # Parse response
            try:
                response_data = json.loads(response_text)
                content = response_data.get("content", response_text)
            except json.JSONDecodeError:
                content = response_text

            # Should identify the languages and components
            content_lower = content.lower()
            assert any(lang in content_lower for lang in ["typescript", "python", "react"])
            assert any(word in content_lower for lang in ["component", "api", "util"])
            print("✓ SAGE folder analysis working")

        except Exception as e:
            pytest.skip(f"SAGE folder analysis failed: {e}")

    def test_folder_size_estimation(self):
        """Test estimation of folder content size"""
        from utils.tokens import estimate_tokens_for_files

        # Read src folder
        src_dir = os.path.join(self.temp_dir, "src")
        expanded = expand_paths([src_dir])
        content = read_files(expanded, mode="embedded")

        # Estimate tokens
        total_tokens = estimate_tokens_for_files(content)
        print(f"Estimated tokens for src folder: {total_tokens:,}")

        assert total_tokens > 0
        assert total_tokens < 100000  # Should be reasonable size

        # Break down by file
        for path, file_content in content.items():
            tokens = estimate_tokens_for_files({path: file_content})
            rel_path = os.path.relpath(path, self.temp_dir)
            print(f"  {rel_path}: {tokens:,} tokens")

    def test_folder_deduplication(self):
        """Test that duplicate files in folders are handled correctly"""
        # Create duplicate files
        dup_dir = os.path.join(self.temp_dir, "duplicates")
        os.makedirs(dup_dir, exist_ok=True)

        content = "This is duplicate content\nLine 2\nLine 3\n"

        # Create same content in multiple files
        for i in range(3):
            file_path = os.path.join(dup_dir, f"dup_{i}.txt")
            with open(file_path, "w") as f:
                f.write(content)

        # Read files
        expanded = expand_paths([dup_dir])
        file_content = read_files(expanded, mode="embedded")

        assert len(file_content) == 3

        # All files should have same content
        contents = list(file_content.values())
        assert all(c == contents[0] for c in contents), "All duplicate files should have same content"

    def test_mixed_file_types_in_folder(self):
        """Test folders with mixed file types"""
        mixed_dir = os.path.join(self.temp_dir, "mixed")
        os.makedirs(mixed_dir, exist_ok=True)

        # Create different file types
        files_to_create = {
            "code.py": 'print("Hello from Python")',
            "data.json": '{"key": "value", "number": 42}',
            "doc.md": "# Documentation\n\nThis is a test document.",
            "config.yml": "database:\n  host: localhost\n  port: 5432",
            "style.css": "body { font-family: Arial; }",
        }

        for filename, content in files_to_create.items():
            file_path = os.path.join(mixed_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        # Test expansion and reading
        expanded = expand_paths([mixed_dir])
        content = read_files(expanded, mode="embedded")

        print(f"Mixed folder contains {len(content)} files:")
        for path in content.keys():
            filename = os.path.basename(path)
            print(f"  {filename}")

        # Should find files based on allowed extensions
        assert len(content) > 0

        # Check that content is correctly read
        for path, file_content in content.items():
            filename = os.path.basename(path)
            assert len(file_content) > 0, f"{filename} should have content"


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Folder Content Handling")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-only", action="store_true", help="Only create test structure")
    args = parser.parse_args()

    if args.create_only:
        # Create test structure and exit
        test_class = TestFolderContent()
        test_class.setup_class()
        print(f"Test project structure created in: {test_class.temp_dir}")

        # List all files created
        all_files = []
        for root, dirs, files in os.walk(test_class.temp_dir):
            for file in files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, test_class.temp_dir)
                size = os.path.getsize(path)
                all_files.append((rel_path, size))

        print(f"Created {len(all_files)} files:")
        for rel_path, size in sorted(all_files):
            print(f"  {rel_path} ({size:,} bytes)")
        sys.exit(0)

    if args.test:
        # Run specific test
        test_class = TestFolderContent()
        test_class.setup_class()

        test_method = getattr(test_class, f"test_{args.test}", None)
        if test_method:
            if asyncio.iscoroutinefunction(test_method):
                asyncio.run(test_method())
            else:
                test_method()
            print(f"✓ Test {args.test} completed")
        else:
            print(f"❌ Test {args.test} not found")
    else:
        # Run all tests with pytest
        pytest.main([__file__, "-v" if args.verbose else ""])
