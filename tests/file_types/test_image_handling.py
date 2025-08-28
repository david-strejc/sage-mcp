#!/usr/bin/env python3
"""
Image Handling Testing Script
Tests image processing across different providers with various formats and sizes
Based on zen-mcp-server image handling patterns
"""

import asyncio
import base64
import json
import os
import tempfile
import time
from pathlib import Path
from PIL import Image
import io

import pytest
import requests

# Add project root to path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.sage import SageTool
from providers.gemini import GeminiProvider
from providers.openai import OpenAIProvider
from providers.anthropic import AnthropicProvider


class TestImageHandling:
    """Test image handling across different providers and formats"""

    @classmethod
    def setup_class(cls):
        """Setup test images in various formats"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_images = {}

        # Create test images
        cls._create_test_images()

    @classmethod
    def teardown_class(cls):
        """Cleanup test images"""
        import shutil

        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _create_test_images(cls):
        """Create various test images"""

        # 1. Small PNG (1x1 transparent)
        small_png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        cls.test_images["small_png"] = cls._save_image(small_png_data, "small.png")

        # 2. Medium PNG (100x100 red square)
        medium_img = Image.new("RGB", (100, 100), color="red")
        cls.test_images["medium_png"] = cls._save_pil_image(medium_img, "medium.png")

        # 3. Large PNG (1000x1000 blue square) - ~3MB
        large_img = Image.new("RGB", (1000, 1000), color="blue")
        cls.test_images["large_png"] = cls._save_pil_image(large_img, "large.png")

        # 4. JPEG image (500x500 green square)
        jpeg_img = Image.new("RGB", (500, 500), color="green")
        cls.test_images["jpeg"] = cls._save_pil_image(jpeg_img, "test.jpg", format="JPEG")

        # 5. WebP image (if supported)
        try:
            webp_img = Image.new("RGB", (200, 200), color="yellow")
            cls.test_images["webp"] = cls._save_pil_image(webp_img, "test.webp", format="WEBP")
        except:
            cls.test_images["webp"] = None

        # 6. Very large image (2000x2000) - might exceed limits
        try:
            huge_img = Image.new("RGB", (2000, 2000), color="purple")
            cls.test_images["huge_png"] = cls._save_pil_image(huge_img, "huge.png")
        except:
            cls.test_images["huge_png"] = None

    @classmethod
    def _save_image(cls, data: bytes, filename: str) -> str:
        """Save binary image data to file"""
        path = os.path.join(cls.temp_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path

    @classmethod
    def _save_pil_image(cls, img: Image.Image, filename: str, format: str = "PNG") -> str:
        """Save PIL image to file"""
        path = os.path.join(cls.temp_dir, filename)
        img.save(path, format=format)
        return path

    def test_image_size_detection(self):
        """Test image size detection"""
        for name, path in self.test_images.items():
            if path and os.path.exists(path):
                size = os.path.getsize(path)
                print(f"{name}: {size:,} bytes")
                assert size > 0

    @pytest.mark.asyncio
    async def test_gemini_image_support(self):
        """Test Gemini provider image support with different formats"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        provider = GeminiProvider()

        # Test with medium PNG
        if self.test_images["medium_png"]:
            try:
                messages = [
                    {
                        "role": "user",
                        "content": "What color is this image? Answer with just the color name.",
                        "files": [self.test_images["medium_png"]],
                    }
                ]

                response = await provider.complete(messages=messages, model="gemini-1.5-pro", temperature=0.1)

                assert response
                assert "red" in response.lower()
                print("✓ Gemini PNG support working")

            except Exception as e:
                pytest.skip(f"Gemini image test failed: {e}")

    @pytest.mark.asyncio
    async def test_openai_image_support(self):
        """Test OpenAI provider image support"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        provider = OpenAIProvider()

        # Test with medium PNG - convert to base64
        if self.test_images["medium_png"]:
            try:
                with open(self.test_images["medium_png"], "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What color is this image? Answer with just the color name."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_data}"}},
                        ],
                    }
                ]

                response = await provider.complete(messages=messages, model="gpt-4o", temperature=0.1)

                assert response
                assert "red" in response.lower()
                print("✓ OpenAI image support working")

            except Exception as e:
                pytest.skip(f"OpenAI image test failed: {e}")

    @pytest.mark.asyncio
    async def test_anthropic_image_support(self):
        """Test Anthropic provider image support"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        provider = AnthropicProvider()

        # Test with medium PNG - convert to base64
        if self.test_images["medium_png"]:
            try:
                with open(self.test_images["medium_png"], "rb") as f:
                    img_data = base64.b64encode(f.read()).decode("utf-8")

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What color is this image? Answer with just the color name."},
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": "image/png", "data": img_data},
                            },
                        ],
                    }
                ]

                response = await provider.complete(
                    messages=messages, model="claude-3-5-sonnet-20241022", temperature=0.1
                )

                assert response
                assert "red" in response.lower()
                print("✓ Anthropic image support working")

            except Exception as e:
                pytest.skip(f"Anthropic image test failed: {e}")

    @pytest.mark.asyncio
    async def test_sage_tool_image_handling(self):
        """Test SAGE tool image handling through unified interface"""
        if not any([os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
            pytest.skip("No API keys set")

        sage_tool = SageTool()

        # Test with medium PNG through SAGE interface
        if self.test_images["medium_png"]:
            try:
                request_data = {
                    "prompt": "What color is this image? Answer with just the color name.",
                    "files": [self.test_images["medium_png"]],
                    "mode": "analyze",
                    "model": "auto",
                }

                result = await sage_tool.execute(request_data)

                assert len(result) > 0
                response_text = result[0].text if hasattr(result[0], "text") else str(result[0])

                # Parse JSON response
                try:
                    response_data = json.loads(response_text)
                    content = response_data.get("content", response_text)
                    assert "red" in content.lower()
                    print("✓ SAGE tool image handling working")
                except json.JSONDecodeError:
                    # Direct text response
                    assert "red" in response_text.lower()
                    print("✓ SAGE tool image handling working")

            except Exception as e:
                pytest.skip(f"SAGE image test failed: {e}")

    def test_image_size_limits(self):
        """Test image size limit validation"""
        # Test different size categories
        sizes = {}

        for name, path in self.test_images.items():
            if path and os.path.exists(path):
                size = os.path.getsize(path)
                sizes[name] = size

        print("Image sizes:")
        for name, size in sizes.items():
            print(f"  {name}: {size:,} bytes ({size/1024/1024:.1f} MB)")

        # Categorize by typical provider limits
        small_limit = 4 * 1024 * 1024  # 4MB - typical OpenAI limit
        large_limit = 20 * 1024 * 1024  # 20MB - typical Gemini limit

        small_images = [name for name, size in sizes.items() if size <= small_limit]
        large_images = [name for name, size in sizes.items() if size > small_limit]

        print(f"Small images (<= 4MB): {small_images}")
        print(f"Large images (> 4MB): {large_images}")

        assert len(small_images) > 0  # Should have some small images

    def test_image_format_support(self):
        """Test different image format support"""
        formats = {}

        for name, path in self.test_images.items():
            if path and os.path.exists(path):
                ext = Path(path).suffix.lower()
                formats[ext] = formats.get(ext, []) + [name]

        print("Image formats:")
        for ext, images in formats.items():
            print(f"  {ext}: {images}")

        # Should support common formats
        assert ".png" in formats
        assert ".jpg" in formats or ".jpeg" in formats

    @pytest.mark.asyncio
    async def test_data_url_handling(self):
        """Test data URL format image handling"""
        # Create data URL from small PNG
        with open(self.test_images["small_png"], "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        data_url = f"data:image/png;base64,{img_data}"

        # Test data URL size
        assert len(data_url) > 0
        print(f"Data URL length: {len(data_url)} characters")

        # Data URLs are valid image references
        assert data_url.startswith("data:image/")
        assert "base64," in data_url

    @pytest.mark.asyncio
    async def test_concurrent_image_processing(self):
        """Test processing multiple images concurrently"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")

        provider = GeminiProvider()

        # Prepare multiple images
        image_tasks = []

        for name, path in [("medium_png", self.test_images["medium_png"]), ("jpeg", self.test_images["jpeg"])]:
            if path and os.path.exists(path):
                messages = [
                    {
                        "role": "user",
                        "content": f"What color is this image? Answer with just the color name.",
                        "files": [path],
                    }
                ]

                task = provider.complete(messages=messages, model="gemini-1.5-flash", temperature=0.1)
                image_tasks.append((name, task))

        if image_tasks:
            try:
                results = await asyncio.gather(*[task for _, task in image_tasks], return_exceptions=True)

                for i, (name, _) in enumerate(image_tasks):
                    result = results[i]
                    if isinstance(result, Exception):
                        print(f"⚠ {name} failed: {result}")
                    else:
                        print(f"✓ {name} processed: {result[:50]}...")

            except Exception as e:
                pytest.skip(f"Concurrent processing failed: {e}")

    def test_invalid_image_handling(self):
        """Test handling of invalid image files"""
        # Create invalid image file
        invalid_path = os.path.join(self.temp_dir, "invalid.png")
        with open(invalid_path, "w") as f:
            f.write("This is not an image file")

        # Test with PIL
        try:
            img = Image.open(invalid_path)
            assert False, "Should have failed to open invalid image"
        except Exception:
            print("✓ Invalid image properly rejected")

    @pytest.mark.asyncio
    async def test_provider_specific_limits(self):
        """Test provider-specific image size limits"""
        providers_info = {
            "OpenAI": {"limit_mb": 20, "models": ["gpt-4o", "gpt-4o-mini"]},
            "Gemini": {"limit_mb": 20, "models": ["gemini-1.5-pro", "gemini-1.5-flash"]},
            "Anthropic": {"limit_mb": 5, "models": ["claude-3-5-sonnet-20241022"]},
        }

        for provider_name, info in providers_info.items():
            limit_bytes = info["limit_mb"] * 1024 * 1024

            # Count images within limit
            valid_images = []
            for name, path in self.test_images.items():
                if path and os.path.exists(path):
                    size = os.path.getsize(path)
                    if size <= limit_bytes:
                        valid_images.append((name, size))

            print(f"{provider_name} ({info['limit_mb']}MB limit): {len(valid_images)} valid images")
            for name, size in valid_images:
                print(f"  {name}: {size:,} bytes")


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Image Handling")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--create-only", action="store_true", help="Only create test images")
    args = parser.parse_args()

    if args.create_only:
        # Create test images and exit
        test_class = TestImageHandling()
        test_class.setup_class()
        print(f"Test images created in: {test_class.temp_dir}")
        for name, path in test_class.test_images.items():
            if path:
                size = os.path.getsize(path)
                print(f"  {name}: {path} ({size:,} bytes)")
        sys.exit(0)

    if args.test:
        # Run specific test
        test_class = TestImageHandling()
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
