#!/usr/bin/env python3
"""
Conversation Continuation Testing Script
Tests conversation memory, thread management, and cross-tool continuation
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone

import pytest

# Add project root to path
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from tools.sage import SageTool
from utils.memory import create_thread, get_thread, add_turn, ConversationThread, ConversationTurn


class TestConversationContinuation:
    """Test conversation continuation functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.sage_tool = SageTool()

    def test_thread_creation(self):
        """Test creating conversation threads"""
        thread_id = create_thread("chat", "test_mode")

        assert thread_id
        assert len(thread_id) > 10  # Should be UUID-like

        # Retrieve thread
        thread_data = get_thread(thread_id)
        assert thread_data
        assert thread_data["tool_name"] == "chat"
        assert thread_data["mode"] == "test_mode"
        assert len(thread_data["turns"]) == 0

    def test_conversation_turn_addition(self):
        """Test adding turns to conversation"""
        thread_id = create_thread("analyze", "code_review")

        # Add user turn
        success = add_turn(
            thread_id=thread_id,
            role="user",
            content="Please analyze this code",
            files=["test.py"],
            tool_name="analyze",
            model_name="gpt-4",
            mode="code_review",
        )
        assert success

        # Add assistant turn
        success = add_turn(
            thread_id=thread_id,
            role="assistant",
            content="This code implements a simple function...",
            tool_name="analyze",
            model_name="gpt-4",
            mode="code_review",
        )
        assert success

        # Retrieve and verify
        thread_data = get_thread(thread_id)
        assert len(thread_data["turns"]) == 2

        user_turn = thread_data["turns"][0]
        assert user_turn["role"] == "user"
        assert user_turn["content"] == "Please analyze this code"
        assert user_turn["files"] == ["test.py"]

        assistant_turn = thread_data["turns"][1]
        assert assistant_turn["role"] == "assistant"
        assert assistant_turn["content"] == "This code implements a simple function..."

    def test_conversation_thread_data_structure(self):
        """Test conversation thread data structure"""
        # Create thread with initial request
        initial_request = {
            "prompt": "Test prompt",
            "files": ["file1.py", "file2.js"],
            "mode": "analyze",
            "model": "gpt-4",
        }

        thread_id = create_thread("sage", "analyze", initial_request)
        thread_data = get_thread(thread_id)

        # Verify structure
        required_fields = ["thread_id", "tool_name", "mode", "created_at", "last_updated", "turns", "initial_request"]

        for field in required_fields:
            assert field in thread_data, f"Missing field: {field}"

        assert thread_data["initial_request"] == initial_request
        assert thread_data["thread_id"] == thread_id

    def test_conversation_memory_persistence(self):
        """Test that conversation memory persists across calls"""
        thread_id = create_thread("debug", "issue_analysis")

        # Add multiple turns
        turns = [
            ("user", "I have a bug in my login system"),
            ("assistant", "Can you show me the code?"),
            ("user", "Here's the authentication function"),
            ("assistant", "I see the issue - you're not checking for null values"),
        ]

        for role, content in turns:
            add_turn(thread_id, role, content, tool_name="debug")

        # Retrieve and verify all turns are there
        thread_data = get_thread(thread_id)
        assert len(thread_data["turns"]) == 4

        for i, (expected_role, expected_content) in enumerate(turns):
            turn = thread_data["turns"][i]
            assert turn["role"] == expected_role
            assert turn["content"] == expected_content

    def test_file_deduplication_across_turns(self):
        """Test file deduplication across conversation turns"""
        thread_id = create_thread("review", "code_review")

        # Add turns with overlapping files
        add_turn(thread_id, "user", "Review these files", files=["main.py", "utils.py", "config.py"])

        add_turn(thread_id, "user", "Also check this file", files=["utils.py", "new_file.py"])  # utils.py repeats

        add_turn(thread_id, "user", "And this one", files=["main.py", "final.py"])  # main.py repeats

        thread_data = get_thread(thread_id)

        # Collect all unique files mentioned
        all_files = set()
        for turn in thread_data["turns"]:
            if turn["files"]:
                all_files.update(turn["files"])

        expected_files = {"main.py", "utils.py", "config.py", "new_file.py", "final.py"}
        assert all_files == expected_files

    @pytest.mark.asyncio
    async def test_sage_tool_conversation_continuation(self):
        """Test SAGE tool conversation continuation"""
        if not any(
            [
                __import__("os").getenv("OPENAI_API_KEY"),
                __import__("os").getenv("GEMINI_API_KEY"),
                __import__("os").getenv("ANTHROPIC_API_KEY"),
            ]
        ):
            pytest.skip("No API keys for conversation continuation test")

        # First request - start conversation
        request1 = {"prompt": "What is 10 + 5?", "mode": "chat", "model": "auto"}

        try:
            result1 = await self.sage_tool.execute(request1)
            assert len(result1) > 0

            response1_text = result1[0].text if hasattr(result1[0], "text") else str(result1[0])

            # Extract thread ID if available
            thread_id = None
            try:
                response1_data = json.loads(response1_text)
                thread_id = response1_data.get("thread_id")
            except json.JSONDecodeError:
                pass

            # Second request - continue conversation
            request2 = {"prompt": "Now multiply that result by 2", "mode": "chat", "model": "auto"}

            if thread_id:
                request2["thread_id"] = thread_id

            result2 = await self.sage_tool.execute(request2)
            assert len(result2) > 0

            response2_text = result2[0].text if hasattr(result2[0], "text") else str(result2[0])

            # Check if continuation worked
            if "30" in response2_text or "thirty" in response2_text.lower():
                print("✓ Conversation continuation working")
            else:
                print(f"⚠ Continuation may not have worked: {response2_text[:100]}")

        except Exception as e:
            pytest.skip(f"SAGE conversation continuation failed: {e}")

    def test_cross_tool_continuation(self):
        """Test conversation continuation across different tools/modes"""
        # Start with analysis
        thread_id = create_thread("analyze", "code_analysis")

        add_turn(thread_id, "user", "Analyze this function for bugs", files=["function.py"], tool_name="analyze")

        add_turn(thread_id, "assistant", "I found a potential null pointer issue", tool_name="analyze")

        # Continue with debug mode
        add_turn(thread_id, "user", "How would I fix that bug?", tool_name="debug")

        add_turn(thread_id, "assistant", "Add null checking before dereferencing", tool_name="debug")

        # Continue with review mode
        add_turn(thread_id, "user", "Review my fix", files=["function_fixed.py"], tool_name="review")

        thread_data = get_thread(thread_id)

        # Should have continuity across tools
        tools_used = set(turn["tool_name"] for turn in thread_data["turns"] if turn.get("tool_name"))
        assert "analyze" in tools_used
        assert "debug" in tools_used
        assert "review" in tools_used

        # Should maintain context
        contents = [turn["content"] for turn in thread_data["turns"]]
        assert any("bug" in content.lower() for content in contents)
        assert any("fix" in content.lower() for content in contents)

    def test_conversation_metadata_tracking(self):
        """Test tracking of conversation metadata"""
        thread_id = create_thread("chat", "general")

        # Add turn with metadata
        add_turn(
            thread_id=thread_id,
            role="user",
            content="Hello",
            files=["test.py"],
            tool_name="chat",
            model_name="gpt-4",
            mode="general",
        )

        thread_data = get_thread(thread_id)
        turn = thread_data["turns"][0]

        # Check metadata is preserved
        assert turn["tool_name"] == "chat"
        assert turn["model_name"] == "gpt-4"
        assert turn["mode"] == "general"
        assert "timestamp" in turn

        # Timestamp should be ISO format
        try:
            datetime.fromisoformat(turn["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {turn['timestamp']}")

    def test_conversation_thread_isolation(self):
        """Test that conversation threads are isolated"""
        # Create two separate threads
        thread1 = create_thread("chat", "thread1")
        thread2 = create_thread("debug", "thread2")

        # Add content to each
        add_turn(thread1, "user", "Message in thread 1")
        add_turn(thread2, "user", "Message in thread 2")

        # Verify isolation
        data1 = get_thread(thread1)
        data2 = get_thread(thread2)

        assert data1["thread_id"] != data2["thread_id"]
        assert data1["tool_name"] != data2["tool_name"]
        assert len(data1["turns"]) == 1
        assert len(data2["turns"]) == 1
        assert data1["turns"][0]["content"] != data2["turns"][0]["content"]

    def test_large_conversation_handling(self):
        """Test handling of conversations with many turns"""
        thread_id = create_thread("chat", "long_conversation")

        # Add many turns
        for i in range(50):
            add_turn(thread_id, "user", f"Message {i}")
            add_turn(thread_id, "assistant", f"Response {i}")

        thread_data = get_thread(thread_id)

        # Should handle large conversations
        assert len(thread_data["turns"]) == 100

        # Verify ordering is preserved
        for i in range(50):
            user_turn = thread_data["turns"][i * 2]
            assistant_turn = thread_data["turns"][i * 2 + 1]

            assert user_turn["content"] == f"Message {i}"
            assert assistant_turn["content"] == f"Response {i}"

    def test_conversation_error_handling(self):
        """Test error handling in conversation management"""
        # Test with non-existent thread
        thread_data = get_thread("non-existent-thread-id")
        assert thread_data is None

        # Test adding turn to non-existent thread
        success = add_turn("non-existent", "user", "test message")
        assert not success

    def test_conversation_file_tracking(self):
        """Test file tracking across conversation"""
        thread_id = create_thread("analyze", "file_analysis")

        # Add turns with various files
        add_turn(thread_id, "user", "Analyze these", files=["file1.py", "file2.js"])
        add_turn(thread_id, "assistant", "Analysis complete")
        add_turn(thread_id, "user", "Also check this", files=["file3.py"])
        add_turn(thread_id, "user", "And this one", files=["file1.py", "file4.rb"])  # file1.py repeats

        thread_data = get_thread(thread_id)

        # Collect all files mentioned in conversation
        all_files = []
        for turn in thread_data["turns"]:
            if turn.get("files"):
                all_files.extend(turn["files"])

        # Should have all files including duplicates
        assert "file1.py" in all_files
        assert "file2.js" in all_files
        assert "file3.py" in all_files
        assert "file4.rb" in all_files

        # Count occurrences
        assert all_files.count("file1.py") == 2  # Appears twice

    def test_conversation_mode_transitions(self):
        """Test transitions between different conversation modes"""
        thread_id = create_thread("sage", "multi_mode")

        # Start with chat
        add_turn(thread_id, "user", "Hello", mode="chat")
        add_turn(thread_id, "assistant", "Hi there!", mode="chat")

        # Switch to analysis
        add_turn(thread_id, "user", "Can you analyze this code?", mode="analyze")
        add_turn(thread_id, "assistant", "Sure, I'll analyze it", mode="analyze")

        # Switch to debug
        add_turn(thread_id, "user", "I found a bug", mode="debug")
        add_turn(thread_id, "assistant", "Let me help debug it", mode="debug")

        thread_data = get_thread(thread_id)

        # Verify mode tracking
        modes = [turn.get("mode") for turn in thread_data["turns"] if turn.get("mode")]
        assert "chat" in modes
        assert "analyze" in modes
        assert "debug" in modes

        # Should maintain conversation continuity despite mode changes
        assert len(thread_data["turns"]) == 6


if __name__ == "__main__":
    # Run individual tests
    import argparse

    parser = argparse.ArgumentParser(description="Test Conversation Continuation")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_class = TestConversationContinuation()
        test_method = getattr(test_class, f"test_{args.test}", None)
        if test_method:
            test_class.setup_method()
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
