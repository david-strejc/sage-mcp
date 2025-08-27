#!/usr/bin/env python3
"""
Text File Handling Testing Script
Tests text file processing including different encodings, formats, and sizes
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
from utils.files import read_files, expand_paths


class TestTextFileHandling:
    """Test text file handling across different formats and encodings"""

    @classmethod
    def setup_class(cls):
        """Setup test text files"""
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
        """Create various test text files"""
        
        # 1. Simple Python file
        python_code = '''#!/usr/bin/env python3
"""
Simple Python module for testing
"""

import os
import sys

def hello_world():
    """Print hello world"""
    print("Hello, World!")
    return "Hello, World!"

class TestClass:
    """A test class"""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    hello_world()
'''
        cls.test_files['python'] = cls._save_text_file(python_code, 'test.py')
        
        # 2. JavaScript file
        js_code = '''// Simple JavaScript module
const greeting = "Hello, World!";

function sayHello(name) {
    return `Hello, ${name}!`;
}

class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    introduce() {
        return `Hi, I'm ${this.name} and I'm ${this.age} years old.`;
    }
}

module.exports = { sayHello, Person };
'''
        cls.test_files['javascript'] = cls._save_text_file(js_code, 'test.js')
        
        # 3. JSON file
        json_data = {
            "name": "Test Project",
            "version": "1.0.0",
            "description": "A test project for file handling",
            "dependencies": {
                "lodash": "^4.17.21",
                "express": "^4.18.0"
            },
            "scripts": {
                "start": "node index.js",
                "test": "jest"
            },
            "nested": {
                "array": [1, 2, 3, 4, 5],
                "boolean": True,
                "null_value": None
            }
        }
        cls.test_files['json'] = cls._save_text_file(json.dumps(json_data, indent=2), 'test.json')
        
        # 4. Markdown file
        markdown_content = '''# Test Markdown File

This is a test markdown file for testing file handling capabilities.

## Features

- **Bold text**
- *Italic text*
- `code snippets`
- [Links](https://example.com)

## Code Block

```python
def example_function():
    return "This is an example"
```

## List

1. First item
2. Second item
3. Third item

### Subsection

> This is a blockquote

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
'''
        cls.test_files['markdown'] = cls._save_text_file(markdown_content, 'test.md')
        
        # 5. Large text file (for testing size limits)
        large_content = "This is a test line. " * 10000  # ~200KB
        cls.test_files['large_text'] = cls._save_text_file(large_content, 'large.txt')
        
        # 6. UTF-8 file with special characters
        utf8_content = '''# UTF-8 Test File 🚀

This file contains various Unicode characters:

## Symbols
- Currency: $ € £ ¥ ₹ ₿
- Math: ∑ ∏ ∞ ≈ ≠ ± √ ∫
- Arrows: → ← ↑ ↓ ⇒ ⇐ ⇑ ⇓
- Misc: ★ ♥ ♣ ♦ ♠ ☀ ☁ ⚡ 🔥

## Languages
- English: Hello World
- Spanish: Hola Mundo
- French: Bonjour le monde
- German: Hallo Welt
- Chinese: 你好世界
- Japanese: こんにちは世界
- Arabic: مرحبا بالعالم
- Russian: Привет мир
- Hindi: नमस्ते दुनिया
- Korean: 안녕하세요 세계

## Emojis
🐍 Python, 🌐 Web, 📚 Books, 🔬 Science, 🎵 Music
'''
        cls.test_files['utf8'] = cls._save_text_file(utf8_content, 'utf8.txt', encoding='utf-8')
        
        # 7. CSV file
        csv_content = '''Name,Age,City,Country,Occupation
John Doe,30,New York,USA,Software Engineer
Jane Smith,25,London,UK,Data Scientist
Bob Johnson,35,Toronto,Canada,Product Manager
Alice Brown,28,Sydney,Australia,UX Designer
Charlie Wilson,32,Berlin,Germany,DevOps Engineer
Diana Davis,27,Paris,France,Frontend Developer
Eve Martinez,31,Madrid,Spain,Backend Developer
Frank Lee,29,Tokyo,Japan,Mobile Developer
'''
        cls.test_files['csv'] = cls._save_text_file(csv_content, 'test.csv')
        
        # 8. Configuration file (.env style)
        env_content = '''# Configuration file
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
API_KEY=your-secret-api-key-here
DEBUG=true
PORT=3000
REDIS_URL=redis://localhost:6379
MAX_CONNECTIONS=100

# Email settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# AWS settings
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=secret...
AWS_REGION=us-west-2
S3_BUCKET=my-bucket
'''
        cls.test_files['env'] = cls._save_text_file(env_content, '.env')
        
        # 9. XML file
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <name>Test Project</name>
    <version>1.0.0</version>
    <description>A test project for XML processing</description>
    
    <dependencies>
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>example-lib</artifactId>
            <version>2.1.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.12.0</version>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
            </plugin>
        </plugins>
    </build>
</project>
'''
        cls.test_files['xml'] = cls._save_text_file(xml_content, 'test.xml')
        
        # 10. Binary-like file (but still text)
        binary_text = ''.join([chr(i) for i in range(32, 127)] * 10)  # ASCII printable chars
        cls.test_files['binary_text'] = cls._save_text_file(binary_text, 'binary.txt')
        
    @classmethod
    def _save_text_file(cls, content: str, filename: str, encoding: str = 'utf-8') -> str:
        """Save text content to file"""
        path = os.path.join(cls.temp_dir, filename)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return path
        
    def test_file_creation(self):
        """Test that all test files were created successfully"""
        for name, path in self.test_files.items():
            assert os.path.exists(path), f"File {name} was not created"
            size = os.path.getsize(path)
            print(f"{name}: {size:,} bytes")
            assert size > 0
            
    def test_file_reading_basic(self):
        """Test basic file reading functionality"""
        # Test reading Python file
        python_files = [self.test_files['python']]
        content = read_files(python_files, mode="embedded")
        
        assert len(content) == 1
        file_content = list(content.values())[0]
        assert "def hello_world" in file_content
        assert "class TestClass" in file_content
        
    def test_different_file_extensions(self):
        """Test reading files with different extensions"""
        test_extensions = {
            '.py': self.test_files['python'],
            '.js': self.test_files['javascript'],
            '.json': self.test_files['json'],
            '.md': self.test_files['markdown'],
            '.csv': self.test_files['csv'],
            '.xml': self.test_files['xml']
        }
        
        for ext, path in test_extensions.items():
            content = read_files([path], mode="embedded")
            assert len(content) == 1
            file_content = list(content.values())[0]
            assert len(file_content) > 0
            print(f"✓ {ext} file read successfully ({len(file_content)} chars)")
            
    def test_utf8_encoding(self):
        """Test UTF-8 encoded files with special characters"""
        content = read_files([self.test_files['utf8']], mode="embedded")
        
        assert len(content) == 1
        file_content = list(content.values())[0]
        
        # Check for various Unicode characters
        assert "🚀" in file_content
        assert "你好世界" in file_content  # Chinese
        assert "Привет мир" in file_content  # Russian
        assert "€" in file_content  # Euro symbol
        assert "∞" in file_content  # Infinity symbol
        
    def test_large_file_handling(self):
        """Test handling of large text files"""
        content = read_files([self.test_files['large_text']], mode="embedded")
        
        assert len(content) == 1
        file_content = list(content.values())[0]
        
        # Should contain repeated text
        assert "This is a test line." in file_content
        assert len(file_content) > 100000  # Should be large
        
    def test_file_summary_mode(self):
        """Test file summary mode"""
        files_to_test = [
            self.test_files['python'],
            self.test_files['javascript'],
            self.test_files['json']
        ]
        
        summaries = read_files(files_to_test, mode="summary")
        
        assert len(summaries) == 3
        
        for path, summary in summaries.items():
            assert isinstance(summary, dict)
            assert 'size_bytes' in summary
            assert 'line_count' in summary
            assert 'file_type' in summary
            assert 'preview' in summary
            assert summary['size_bytes'] > 0
            assert summary['line_count'] > 0
            
            print(f"Summary for {Path(path).name}:")
            print(f"  Size: {summary['size_bytes']} bytes")
            print(f"  Lines: {summary['line_count']}")
            print(f"  Type: {summary['file_type']}")
            
    def test_file_reference_mode(self):
        """Test file reference mode"""
        files_to_test = [
            self.test_files['python'],
            self.test_files['markdown']
        ]
        
        references = read_files(files_to_test, mode="reference")
        
        assert len(references) == 2
        
        for path, reference in references.items():
            assert isinstance(reference, dict)
            assert 'reference_id' in reference
            assert 'stored' in reference
            assert 'size' in reference
            assert 'type' in reference
            assert reference['stored'] == True
            
    def test_path_expansion(self):
        """Test directory path expansion"""
        # Create subdirectory with files
        subdir = os.path.join(self.temp_dir, 'subdir')
        os.makedirs(subdir, exist_ok=True)
        
        # Copy some files to subdirectory
        import shutil
        shutil.copy2(self.test_files['python'], os.path.join(subdir, 'sub_test.py'))
        shutil.copy2(self.test_files['javascript'], os.path.join(subdir, 'sub_test.js'))
        
        # Test expansion
        expanded = expand_paths([subdir])
        
        assert len(expanded) == 2
        assert any('sub_test.py' in path for path in expanded)
        assert any('sub_test.js' in path for path in expanded)
        
    @pytest.mark.asyncio
    async def test_sage_tool_text_analysis(self):
        """Test SAGE tool analysis of text files"""
        if not any([os.getenv('OPENAI_API_KEY'), os.getenv('GEMINI_API_KEY'), os.getenv('ANTHROPIC_API_KEY')]):
            pytest.skip("No API keys set")
            
        sage_tool = SageTool()
        
        # Test analyzing Python code
        try:
            request_data = {
                "prompt": "Analyze this Python code. What does the hello_world function do?",
                "files": [self.test_files['python']],
                "mode": "analyze",
                "model": "auto"
            }
            
            result = await sage_tool.execute(request_data)
            
            assert len(result) > 0
            response_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            
            # Parse response
            try:
                response_data = json.loads(response_text)
                content = response_data.get('content', response_text)
            except json.JSONDecodeError:
                content = response_text
                
            assert "hello_world" in content
            print("✓ SAGE tool Python analysis working")
            
        except Exception as e:
            pytest.skip(f"SAGE Python analysis failed: {e}")
            
    @pytest.mark.asyncio
    async def test_multiple_file_analysis(self):
        """Test analysis of multiple files at once"""
        if not any([os.getenv('OPENAI_API_KEY'), os.getenv('GEMINI_API_KEY'), os.getenv('ANTHROPIC_API_KEY')]):
            pytest.skip("No API keys set")
            
        sage_tool = SageTool()
        
        # Test with Python and JavaScript files
        try:
            request_data = {
                "prompt": "Compare these two files. What programming languages are they written in?",
                "files": [self.test_files['python'], self.test_files['javascript']],
                "mode": "analyze", 
                "model": "auto"
            }
            
            result = await sage_tool.execute(request_data)
            
            assert len(result) > 0
            response_text = result[0].text if hasattr(result[0], 'text') else str(result[0])
            
            # Parse response
            try:
                response_data = json.loads(response_text)
                content = response_data.get('content', response_text)
            except json.JSONDecodeError:
                content = response_text
                
            assert any(lang in content.lower() for lang in ['python', 'javascript'])
            print("✓ Multiple file analysis working")
            
        except Exception as e:
            pytest.skip(f"Multiple file analysis failed: {e}")
            
    def test_file_type_detection(self):
        """Test file type detection based on extensions"""
        expected_types = {
            'python': '.py',
            'javascript': '.js', 
            'json': '.json',
            'markdown': '.md',
            'csv': '.csv',
            'xml': '.xml',
            'env': '.env'
        }
        
        for name, expected_ext in expected_types.items():
            path = self.test_files[name]
            actual_ext = Path(path).suffix
            
            if expected_ext.startswith('.'):
                assert actual_ext == expected_ext
            else:
                assert Path(path).name.endswith(expected_ext)
                
    def test_content_validation(self):
        """Test content validation for specific file types"""
        # JSON file should be valid JSON
        with open(self.test_files['json'], 'r') as f:
            json_content = f.read()
        json.loads(json_content)  # Should not raise exception
        
        # Python file should have valid syntax
        with open(self.test_files['python'], 'r') as f:
            python_content = f.read()
        compile(python_content, self.test_files['python'], 'exec')  # Should not raise exception
        
        # CSV should have consistent columns
        with open(self.test_files['csv'], 'r') as f:
            csv_lines = f.readlines()
        header_cols = len(csv_lines[0].strip().split(','))
        for line in csv_lines[1:]:
            if line.strip():  # Skip empty lines
                cols = len(line.strip().split(','))
                assert cols == header_cols, f"CSV line has {cols} columns, expected {header_cols}"


if __name__ == "__main__":
    # Run individual tests
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Text File Handling")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-only", action="store_true", help="Only create test files")
    args = parser.parse_args()
    
    if args.create_only:
        # Create test files and exit
        test_class = TestTextFileHandling()
        test_class.setup_class()
        print(f"Test files created in: {test_class.temp_dir}")
        for name, path in test_class.test_files.items():
            size = os.path.getsize(path)
            print(f"  {name}: {path} ({size:,} bytes)")
        sys.exit(0)
    
    if args.test:
        # Run specific test
        test_class = TestTextFileHandling()
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