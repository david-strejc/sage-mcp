"""
SAGE Universal Tool - One tool to rule them all
Incorporates conversation continuation, smart file handling, and model restrictions
"""

import json
import logging
import os
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field

from mcp.types import TextContent
from config import Config
from modes import get_mode_handler
from providers import get_provider, list_available_models
from utils.files import read_files, expand_paths
from utils.memory import get_thread, add_turn, create_thread
from utils.models import select_best_model, ModelRestrictionService
from utils.security import validate_paths
from models import manager as model_manager

logger = logging.getLogger(__name__)


class SageRequest(BaseModel):
    """Request model for SAGE tool with all critical features"""

    # Core parameters
    mode: str = Field(
        default="chat", description="Operation mode: chat, analyze, review, debug, plan, test, refactor, think"
    )
    prompt: str = Field(..., description="Your question, request, or task description")
    files: Optional[list[str]] = Field(
        default=None,
        description="Files or directories to analyze. Use absolute paths like '/home/user/project/file.py' or relative paths from current directory. Directories will be expanded automatically.",
    )

    # Model selection and restrictions
    model: Optional[str] = Field(
        default=None, description="AI model: USE ONLY gemini-2.5-pro, gemini-2.5-flash, gpt-5, o3, claude-opus-4.1, claude-sonnet-4. NOT gemini-2.0-flash-exp!"
    )
    temperature: Optional[float] = Field(default=None, description="Response creativity (0-1, tool-specific defaults)")
    thinking_mode: Optional[Literal["minimal", "low", "medium", "high", "max"]] = Field(
        default=None,
        description="Thinking depth: minimal=0.5%, low=8%, medium=33%, high=67%, max=100% of model's max thinking tokens",
    )

    # Critical features from zen-mcp
    continuation_id: Optional[str] = Field(
        default=None,
        description="Thread continuation ID for multi-turn conversations. Enables cross-tool conversation continuation.",
    )
    file_handling_mode: Optional[Literal["embedded", "summary", "reference"]] = Field(
        default="embedded",
        description="How to handle file content: 'embedded' includes full content, 'summary' returns summaries, 'reference' stores files with IDs",
    )
    use_websearch: Optional[bool] = Field(
        default=True, description="Enable web search for documentation, best practices, and current information"
    )


class SageTool:
    """Universal AI assistant that can analyze files, debug code, and have conversations.
    Supports multiple AI providers and smart model selection."""

    def __init__(self):
        self.config = Config()
        self.restriction_service = ModelRestrictionService()

    def get_input_schema(self) -> dict[str, Any]:
        """Generate dynamic input schema based on available models and restrictions"""

        # Check if in auto mode for model requirements
        is_auto_mode = self.config.DEFAULT_MODEL.lower() == "auto"

        # Get available models after applying restrictions
        available_models = self._get_available_models()

        schema = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["chat", "analyze", "review", "debug", "plan", "test", "refactor", "think"],
                    "default": "chat",
                    "description": "Operation mode: chat (general Q&A), analyze (code analysis), review (code review), debug (fix issues), plan (architecture), test (generate tests), refactor (improve code), think (deep reasoning)",
                },
                "prompt": {
                    "type": "string",
                    "description": "Your question, request, or what you want to analyze. Examples: 'Review this code for security issues', 'Help me debug this error', 'Explain how this function works'",
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "PROVIDE FILE PATHS ONLY - NOT file contents! Give absolute paths to files/directories you want SAGE to read and analyze (like '/home/user/project/file.py' or '/path/to/folder'). SAGE reads the files FROM DISK using these paths. Do NOT paste file contents - just provide the paths. Directories auto-expand to include relevant files.",
                    "examples": [
                        ["/home/user/project/src/main.py"],
                        ["/workspace/backend", "/workspace/tests"],
                        ["/tmp/debug.log"],
                    ],
                },
                "temperature": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Response creativity (0-1, tool-specific defaults)",
                },
                "thinking_mode": {
                    "type": "string",
                    "enum": ["minimal", "low", "medium", "high", "max"],
                    "description": "Thinking depth: minimal=0.5%, low=8%, medium=33%, high=67%, max=100% of model's max thinking tokens",
                },
                "continuation_id": {
                    "type": "string",
                    "description": "Optional: Continue a previous conversation by providing its ID. SAGE will remember the context and files from that conversation. You'll see this ID in SAGE's responses.",
                },
                "file_handling_mode": {
                    "type": "string",
                    "enum": ["embedded", "summary", "reference"],
                    "default": "embedded",
                    "description": "How files are processed: 'embedded' (full content, best for small files), 'summary' (AI-generated summaries, saves tokens), 'reference' (stores files with IDs for later use)",
                },
                "use_websearch": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable web search for documentation, best practices, and current information.",
                },
            },
            "required": ["prompt"],
        }

        # Add model field with restrictions applied and hints
        if available_models:
            # Get model hints from ModelManager - pass available models for dynamic generation
            model_hints = model_manager.get_tool_description_hints(available_models)

            if is_auto_mode:
                # In auto mode, model is required and shows all available options with hints
                description = f"""REQUIRED: Select the AI model for this task. {model_hints} CRITICAL: You MUST select from the models listed above. Do NOT use model names from your training data. ✅ ONLY use these exact model names: {', '.join(sorted(available_models))} ❌ DO NOT use: gemini-2.0-flash-exp, gemini-2.0-flash-thinking-exp, or any model not listed above"""

                schema["properties"]["model"] = {"type": "string", "enum": available_models, "description": description}
                schema["required"].append("model")
            else:
                # Normal mode, model is optional with available options and hints
                description = f"""AI model to use (optional - defaults to auto-selection). {model_hints} CRITICAL: You MUST select from the models listed above. Do NOT use model names from your training data. ✅ ONLY use these exact model names: {', '.join(sorted(available_models))} ❌ DO NOT use: gemini-2.0-flash-exp, gemini-2.0-flash-thinking-exp, or any model not listed above. Or use "auto" to let SAGE choose the best model for your task."""

                schema["properties"]["model"] = {
                    "type": "string",
                    "enum": available_models + ["auto"],
                    "default": "auto",
                    "description": description,
                }
        else:
            # No models available due to restrictions or missing API keys
            schema["properties"]["model"] = {
                "type": "string",
                "description": "No models available. Please check API keys and model restrictions in environment variables.",
            }

        return schema

    def _get_available_models(self) -> list[str]:
        """Get list of available models after applying restrictions"""
        try:
            all_models_info = list_available_models()
            all_models = all_models_info.get("available_models", [])

            # Apply restrictions
            available_models = []
            for model in all_models:
                if self.restriction_service.is_model_allowed(model):
                    available_models.append(model)

            return available_models
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

    async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
        """
        Execute SAGE tool with comprehensive feature support

        This is the main orchestrator method that coordinates all SAGE operations.
        It delegates specific tasks to focused private methods for better testability.
        """
        try:
            # 1. Validate request and check restrictions
            request = self._validate_request(arguments)

            # 2. Prepare conversation context and get embedded files
            conversation_context, embedded_files = self._prepare_conversation_context(request.continuation_id)

            # 3. Process files with smart deduplication
            file_contents, new_files = self._process_files(
                request.files, embedded_files, request.file_handling_mode, request.model or self.config.DEFAULT_MODEL
            )

            # 4. Select model and get provider
            model_name, provider = self._select_model_and_provider(request, conversation_context, new_files)

            # 5. Get mode handler
            handler = get_mode_handler(request.mode)
            if not handler:
                raise ValueError(f"Unknown mode: {request.mode}")

            # 6. Build context and execute
            full_context = {
                "prompt": request.prompt,
                "files": file_contents,
                "conversation": conversation_context,
                "mode": request.mode,
                "model": model_name,
                "temperature": request.temperature or self.config.TEMPERATURES.get(request.mode, 0.5),
                "thinking_mode": request.thinking_mode,
                "use_websearch": request.use_websearch,
                "file_handling_mode": request.file_handling_mode,
                "embedded_files": embedded_files,
                "new_files": new_files,
            }

            logger.info(f"Executing {request.mode} mode with {model_name}")
            result = await handler.handle(full_context, provider)

            # 7. Update conversation memory
            thread_id = request.continuation_id
            if not thread_id and len(result) > 100:  # Create new thread for substantial responses
                thread_id = create_thread(tool_name="sage", mode=request.mode, initial_request=arguments)
                logger.info(f"Created new conversation thread: {thread_id}")

            if thread_id:
                self._update_conversation_memory(thread_id, request, result, model_name)

                # 8. Format response with continuation offer
                if not request.continuation_id:  # Only for new conversations
                    result = self._format_response(result, thread_id)

            return [TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error in SAGE tool: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": f"SAGE execution failed: {str(e)}"}))]

    def _is_model_allowed(self, model_name: str) -> bool:
        """Check if model is allowed by restriction service"""
        return self.restriction_service.is_model_allowed(model_name)

    def _get_conversation_files(self, conversation_context: dict) -> list[str]:
        """Extract files from conversation context"""
        files = []
        for turn in conversation_context.get("turns", []):
            if turn.get("files"):
                files.extend(turn["files"])
        return list(set(files))  # Remove duplicates

    def _get_token_budget(self, model_name: str) -> int:
        """Get token budget for file reading based on model capabilities"""
        max_tokens = self.config.MAX_TOKENS.get(model_name, self.config.MAX_TOKENS["default"])
        return int(max_tokens * 0.7)  # Reserve 30% for response generation

    def _validate_request(self, arguments: dict) -> SageRequest:
        """Validate and parse request arguments"""
        # Pre-process model name to catch common mistakes
        if "model" in arguments and arguments["model"]:
            original_model = arguments["model"]
            # Common mistaken variations that Claude might use
            model_corrections = {
                "gemini 2.5 pro": "gemini-2.5-pro",
                "gemini-2.5 pro": "gemini-2.5-pro",
                "gemini2.5pro": "gemini-2.5-pro",
                "gemini 2.5 flash": "gemini-2.5-flash",
                "gemini-2.5 flash": "gemini-2.5-flash",
                "gemini2.5flash": "gemini-2.5-flash",
                "gpt5": "gpt-5",
                "gpt 5": "gpt-5",
                "claude opus 4.1": "claude-opus-4.1",
                "claude-opus-4-1": "claude-opus-4.1",
                "claude sonnet 4": "claude-sonnet-4",
                # Block outdated models from Claude's training data
                "gemini-2.0-flash-exp": None,
                "gemini-2.0-flash-thinking-exp": None,
                "gemini-exp-1206": None,
                "gemini-exp-1121": None,
            }
            
            # Check for corrections
            lower_model = original_model.lower().strip()
            if lower_model in model_corrections:
                corrected = model_corrections[lower_model]
                if corrected is None:
                    # This is a blocked model from training data
                    available = self._get_available_models()
                    error_msg = (
                        f"❌ Model '{original_model}' is from outdated training data and not available.\n"
                        f"\n✅ Available models you MUST use: {', '.join(sorted(available))}\n"
                        f"\n⚠️ For Gemini 2.5 Pro, use: 'gemini-2.5-pro'\n"
                        f"⚠️ For Gemini 2.5 Flash, use: 'gemini-2.5-flash'"
                    )
                    raise ValueError(error_msg)
                else:
                    arguments["model"] = corrected
                    logger.info(f"Corrected model name from '{original_model}' to '{corrected}'")
        
        request = SageRequest(**arguments)
        logger.info(f"SAGE {request.mode} mode called")

        # Check model restrictions
        if request.model and not self._is_model_allowed(request.model):
            available = self._get_available_models()
            # Create concise error message for JSON output
            error_msg = (
                f"Model '{request.model}' is not recognized or available. "
                f"\n\n✅ Available models you MUST use: {', '.join(sorted(available))}\n"
                f"\n⚠️ IMPORTANT: Use ONLY the exact model names listed above.\n"
                f"❌ DO NOT use models from your training data like 'gemini-2.0-flash-exp'.\n"
                f"\nFor Gemini 2.5 Pro, use: 'gemini-2.5-pro' (with hyphens, not 'gemini 2.5 pro')"
            )
            raise ValueError(error_msg)

        # Validate file paths for security
        if request.files:
            valid, error = validate_paths(request.files)
            if not valid:
                raise ValueError(f"Invalid file paths: {error}")

        return request

    def _prepare_conversation_context(self, continuation_id: Optional[str]) -> tuple[Optional[dict], list[str]]:
        """Load conversation context and extract embedded files"""
        conversation_context = None
        embedded_files = []

        if continuation_id:
            conversation_context = get_thread(continuation_id)
            if conversation_context:
                embedded_files = self._get_conversation_files(conversation_context)
                logger.info(f"Continuing conversation {continuation_id} with {len(embedded_files)} embedded files")
            else:
                logger.warning(f"Continuation ID {continuation_id} not found")

        return conversation_context, embedded_files

    def _process_files(
        self, files: Optional[list[str]], embedded_files: list[str], file_handling_mode: str, model: str
    ) -> tuple[dict[str, Any], list[str]]:
        """Process files with deduplication and content reading"""
        file_contents = {}
        new_files = []

        if files:
            # Expand directories to individual files
            expanded_files = expand_paths(files)

            # Filter out files already in conversation history
            if embedded_files:
                new_files = [f for f in expanded_files if f not in embedded_files]
                logger.info(
                    f"File deduplication: {len(expanded_files)} total, {len(new_files)} new, {len(embedded_files)} already embedded"
                )
            else:
                new_files = expanded_files

            # Read only new files
            if new_files:
                file_contents = read_files(new_files, mode=file_handling_mode, max_tokens=self._get_token_budget(model))

        return file_contents, new_files

    def _select_model_and_provider(
        self, request: SageRequest, conversation_context: Optional[dict], new_files: list[str]
    ) -> tuple[str, Any]:
        """Select model and get provider instance"""
        model_name = request.model or self.config.DEFAULT_MODEL

        if model_name == "auto" or model_name == "":
            # Use ModelManager for intelligent selection
            allowed_models = self._get_available_models()
            model_name, reasoning = model_manager.select_model_for_task(
                mode=request.mode,
                prompt_size=len(request.prompt),
                file_count=len(new_files),
                conversation_context=conversation_context,
                allowed_models=allowed_models,
            )
            logger.info(f"Auto-selected model: {model_name} - {reasoning}")

        provider = get_provider(model_name)
        if not provider:
            available = self._get_available_models()
            # Create concise error message for JSON output
            error_msg = (
                f"No provider available for model '{model_name}'. \n"
                f"\n✅ Available models you MUST use: {', '.join(sorted(available))}\n"
                f"\n⚠️ Use ONLY these exact model names. DO NOT use models from your training data.\n"
                f"Check API keys are set and use exact model names."
            )
            raise ValueError(error_msg)

        return model_name, provider

    def _update_conversation_memory(self, thread_id: str, request: SageRequest, result: str, model_name: str) -> None:
        """Update conversation memory with request and response"""
        # Add user request
        add_turn(
            thread_id,
            role="user",
            content=request.prompt,
            files=request.files or [],
            tool_name="sage",
            model_name=model_name,
            mode=request.mode,
        )

        # Add assistant response
        add_turn(
            thread_id, role="assistant", content=result, tool_name="sage", model_name=model_name, mode=request.mode
        )

    def _format_response(self, result: str, thread_id: str) -> str:
        """Format final response with continuation offer"""
        return f"""{result}

---
💬 **Continue this conversation**: Use `continuation_id: "{thread_id}"` in your next SAGE call to maintain context and avoid re-reading files."""
