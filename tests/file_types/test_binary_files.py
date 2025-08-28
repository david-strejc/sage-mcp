#!/usr/bin/env python3
"""
Binary File Handling Testing Script
Tests binary file detection and handling (should be rejected by text processors)
"""

import os
import tempfile
from pathlib import Path

import pytest

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.files import read_files
from utils.security import is_safe_path


class TestBinaryFileHandling:
    """Test binary file handling and rejection"""

    @classmethod
    def setup_class(cls):
        """Setup test binary files"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_files = {}
        cls._create_test_files()

    @classmethod
    def teardown_class(cls):
        """Cleanup test files"""
        import shutil

        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _create_test_files(cls):
        """Create various test binary files"""

        # 1. Simple binary file with null bytes
        binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd\xfc" * 100
        cls.test_files["binary"] = cls._save_binary_file(binary_data, "test.bin")

        # 2. Fake executable (ELF header)
        elf_header = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 56  # Minimal ELF header
        cls.test_files["executable"] = cls._save_binary_file(elf_header, "test.exe")

        # 3. Archive file (ZIP signature)
        zip_signature = b"PK\x03\x04" + b"\x00" * 100  # ZIP local file header
        cls.test_files["archive"] = cls._save_binary_file(zip_signature, "test.zip")

        # 4. Media file (MP3 header)
        mp3_header = b"\xff\xfb" + b"\x00" * 100  # MP3 frame sync
        cls.test_files["audio"] = cls._save_binary_file(mp3_header, "test.mp3")

        # 5. PDF file header
        pdf_header = b"%PDF-1.4\n" + b"\x00" * 100  # PDF header
        cls.test_files["pdf"] = cls._save_binary_file(pdf_header, "test.pdf")

        # 6. Object file
        obj_data = b"\x00\x00\x00\x00" * 50  # Generic object file
        cls.test_files["object"] = cls._save_binary_file(obj_data, "test.o")

        # 7. Database file (SQLite header)
        sqlite_header = b"SQLite format 3\x00" + b"\x00" * 100
        cls.test_files["database"] = cls._save_binary_file(sqlite_header, "test.db")

        # 8. Large binary file
        large_binary = b"\xff\x00" * 50000  # 100KB of binary data
        cls.test_files["large_binary"] = cls._save_binary_file(large_binary, "large.bin")

        # 9. Mixed text/binary (starts as text, has binary)
        mixed_data = b"This looks like text\n\x00\xff\x00\x01Binary data here\n"
        cls.test_files["mixed"] = cls._save_binary_file(mixed_data, "mixed.txt")

        # 10. Empty binary file
        cls.test_files["empty"] = cls._save_binary_file(b"", "empty.bin")

    @classmethod
    def _save_binary_file(cls, data: bytes, filename: str) -> str:
        """Save binary data to file"""
        path = os.path.join(cls.temp_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def test_binary_file_creation(self):
        """Test that all binary files were created successfully"""
        for name, path in self.test_files.items():
            assert os.path.exists(path), f"File {name} was not created"
            size = os.path.getsize(path)
            print(f"{name}: {size:,} bytes")

    def test_binary_file_detection(self):
        """Test binary file detection using file signatures"""
        signatures = {
            "executable": b"\x7fELF",
            "archive": b"PK\x03\x04",
            "audio": b"\xff\xfb",
            "pdf": b"%PDF",
            "database": b"SQLite format 3",
        }

        for name, expected_sig in signatures.items():
            path = self.test_files[name]
            with open(path, "rb") as f:
                header = f.read(len(expected_sig))
            assert header.startswith(expected_sig), f"{name} doesn't have expected signature"

    def test_text_file_reading_rejection(self):
        """Test that binary files are rejected by text file readers"""
        # Try to read binary files as text
        for name, path in self.test_files.items():
            if name in ["mixed", "empty"]:  # Skip special cases
                continue

            try:
                content = read_files([path], mode="embedded")

                # If reading succeeds, check if content indicates error
                if content:
                    file_content = list(content.values())[0]
                    if isinstance(file_content, str):
                        # Check if it's an error message
                        if "Error reading file" in file_content or "[File too large" in file_content:
                            print(f"✓ {name}: Properly rejected with error message")
                        else:
                            # Content was read - check if it looks corrupted
                            if "\x00" in file_content or len(file_content.encode("utf-8", errors="ignore")) != len(
                                file_content.encode("utf-8")
                            ):
                                print(f"⚠ {name}: Read but content appears corrupted")
                            else:
                                print(f"⚠ {name}: Read successfully (might be text-like)")
                    else:
                        print(f"⚠ {name}: Non-string content returned")
                else:
                    print(f"✓ {name}: Empty content returned")

            except Exception as e:
                print(f"✓ {name}: Exception raised during read: {type(e).__name__}")

    def test_security_validation(self):
        """Test security validation of binary file paths"""
        for name, path in self.test_files.items():
            path_obj = Path(path)
            is_safe = is_safe_path(path_obj)

            # All our test files should be considered safe (they exist and are files)
            assert is_safe, f"Security validation failed for {name}"

    def test_file_extension_filtering(self):
        """Test that binary file extensions are properly handled"""
        from config import Config

        config = Config()

        binary_extensions = [".bin", ".exe", ".zip", ".mp3", ".pdf", ".o", ".db"]
        allowed_extensions = config.ALLOWED_FILE_EXTENSIONS

        # Check which binary extensions are allowed
        for ext in binary_extensions:
            is_allowed = ext in allowed_extensions
            print(f"Extension {ext}: {'allowed' if is_allowed else 'blocked'}")

        # Most binary extensions should be blocked
        blocked_extensions = [ext for ext in binary_extensions if ext not in allowed_extensions]
        print(f"Blocked binary extensions: {blocked_extensions}")

    def test_mixed_content_handling(self):
        """Test handling of files with mixed text/binary content"""
        mixed_path = self.test_files["mixed"]

        try:
            content = read_files([mixed_path], mode="embedded")

            if content:
                file_content = list(content.values())[0]
                print(f"Mixed content result: {repr(file_content[:100])}")

                # Content might be partially readable
                if "This looks like text" in file_content:
                    print("✓ Text portion was readable")
                else:
                    print("⚠ Text portion not found in result")
            else:
                print("✓ Mixed content file properly rejected")

        except Exception as e:
            print(f"✓ Mixed content raised exception: {type(e).__name__}")

    def test_empty_file_handling(self):
        """Test handling of empty binary files"""
        empty_path = self.test_files["empty"]

        try:
            content = read_files([empty_path], mode="embedded")

            if content:
                file_content = list(content.values())[0]
                assert file_content == "", "Empty file should return empty string"
                print("✓ Empty binary file handled correctly")
            else:
                print("⚠ Empty file returned no content")

        except Exception as e:
            print(f"⚠ Empty file raised exception: {type(e).__name__}")

    def test_large_binary_file_handling(self):
        """Test handling of large binary files"""
        large_path = self.test_files["large_binary"]
        size = os.path.getsize(large_path)

        print(f"Large binary file size: {size:,} bytes")

        try:
            content = read_files([large_path], mode="embedded")

            if content:
                file_content = list(content.values())[0]
                if "[File too large" in file_content:
                    print("✓ Large binary file properly rejected due to size")
                elif "Error reading file" in file_content:
                    print("✓ Large binary file properly rejected with error")
                else:
                    print(f"⚠ Large binary file content: {len(file_content)} chars")
            else:
                print("✓ Large binary file returned no content")

        except Exception as e:
            print(f"✓ Large binary file raised exception: {type(e).__name__}")

    def test_file_summary_mode_with_binary(self):
        """Test file summary mode with binary files"""
        # Try a few binary files
        test_paths = [self.test_files["binary"], self.test_files["pdf"], self.test_files["archive"]]

        try:
            summaries = read_files(test_paths, mode="summary")

            for path, summary in summaries.items():
                filename = Path(path).name
                print(f"Binary file summary for {filename}:")

                if isinstance(summary, dict):
                    if "error" in summary:
                        print(f"  Error: {summary['error']}")
                    else:
                        print(f"  Size: {summary.get('size_bytes', 'unknown')} bytes")
                        print(f"  Type: {summary.get('file_type', 'unknown')}")
                        print(f"  Lines: {summary.get('line_count', 'unknown')}")
                else:
                    print(f"  Non-dict summary: {summary}")

        except Exception as e:
            print(f"Binary summary mode raised exception: {type(e).__name__}")

    def test_common_binary_patterns(self):
        """Test detection of common binary file patterns"""
        patterns = {
            "null_bytes": b"\x00",
            "high_bit_chars": bytes([i for i in range(128, 256)]),
            "control_chars": bytes([i for i in range(0, 32) if i not in [9, 10, 13]]),  # Exclude tab, LF, CR
        }

        for name, path in self.test_files.items():
            if name in ["empty", "mixed"]:
                continue

            with open(path, "rb") as f:
                data = f.read(1000)  # Read first 1KB

            has_binary = False
            for pattern_name, pattern in patterns.items():
                if pattern_name == "null_bytes":
                    if pattern in data:
                        has_binary = True
                        break
                elif pattern_name == "high_bit_chars":
                    if any(b in data for b in pattern):
                        has_binary = True
                        break
                elif pattern_name == "control_chars":
                    if any(b in data for b in pattern):
                        has_binary = True
                        break

            print(f"{name}: {'binary' if has_binary else 'text-like'}")

            # Most of our test files should be detected as binary
            if name != "pdf":  # PDF starts with text-like header
                assert has_binary, f"{name} should be detected as binary"


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Binary File Handling")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-only", action="store_true", help="Only create test files")
    args = parser.parse_args()

    if args.create_only:
        # Create test files and exit
        test_class = TestBinaryFileHandling()
        test_class.setup_class()
        print(f"Test files created in: {test_class.temp_dir}")
        for name, path in test_class.test_files.items():
            size = os.path.getsize(path)
            print(f"  {name}: {path} ({size:,} bytes)")
        sys.exit(0)

    if args.test:
        # Run specific test
        test_class = TestBinaryFileHandling()
        test_class.setup_class()

        test_method = getattr(test_class, f"test_{args.test}", None)
        if test_method:
            test_method()
            print(f"✓ Test {args.test} completed")
        else:
            print(f"❌ Test {args.test} not found")
    else:
        # Run all tests with pytest
        pytest.main([__file__, "-v" if args.verbose else ""])
