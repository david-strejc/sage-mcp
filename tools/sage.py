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

logger = logging.getLogger(__name__)

class SageRequest(BaseModel):
    """Request model for SAGE tool with all critical features"""
    
    # Core parameters
    mode: str = Field(
        default="chat",
        description="Operation mode: chat, analyze, review, debug, plan, test, refactor, think"
    )
    prompt: str = Field(
        ...,
        description="Your question, request, or task description"
    )
    files: Optional[list[str]] = Field(
        default=None,
        description="Files or directories to include (absolute paths). Supports smart deduplication."
    )
    
    # Model selection and restrictions
    model: Optional[str] = Field(
        default=None,
        description="AI model to use. Supports model restrictions via environment variables."
    )
    temperature: Optional[float] = Field(
        default=None,
        description="Response creativity (0-1, tool-specific defaults)"
    )
    thinking_mode: Optional[Literal["minimal", "low", "medium", "high", "max"]] = Field(
        default=None,
        description="Thinking depth: minimal (0.5% of model max), low (8%), medium (33%), high (67%), max (100% of model max)"
    )
    
    # Critical features from zen-mcp
    continuation_id: Optional[str] = Field(
        default=None,
        description="Thread continuation ID for multi-turn conversations. Enables cross-tool conversation continuation."
    )
    file_handling_mode: Optional[Literal["embedded", "summary", "reference"]] = Field(
        default="embedded",
        description="How to handle file content: 'embedded' includes full content, 'summary' returns summaries, 'reference' stores files with IDs"
    )
    use_websearch: Optional[bool] = Field(
        default=True,
        description="Enable web search for documentation, best practices, and current information"
    )

class SageTool:
    """Universal AI assistant tool with conversation continuation and smart file handling"""
    
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
                    "description": "Operation mode - determines the AI's approach and specialization"
                },
                "prompt": {
                    "type": "string", 
                    "description": "Your question, request, or task description"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files or directories to include (absolute paths). Supports automatic directory expansion and smart deduplication across conversation turns."
                },
                "temperature": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Response creativity (0-1, tool-specific defaults)"
                },
                "thinking_mode": {
                    "type": "string",
                    "enum": ["minimal", "low", "medium", "high", "max"],
                    "description": "Thinking depth: minimal (0.5% of model max), low (8%), medium (33%), high (67%), max (100% of model max)"
                },
                "continuation_id": {
                    "type": "string",
                    "description": "Thread continuation ID for multi-turn conversations. Enables seamless conversation continuation across different tools and modes."
                },
                "file_handling_mode": {
                    "type": "string",
                    "enum": ["embedded", "summary", "reference"],
                    "default": "embedded",
                    "description": "How to handle file content in responses. 'embedded' includes full content (default), 'summary' returns only summaries to save tokens, 'reference' stores files and returns IDs."
                },
                "use_websearch": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable web search for documentation, best practices, and current information."
                }
            },
            "required": ["prompt"]
        }
        
        # Add model field with restrictions applied
        if available_models:
            if is_auto_mode:
                # In auto mode, model is required and shows all available options
                schema["properties"]["model"] = {
                    "type": "string",
                    "enum": available_models,
                    "description": "REQUIRED: Select the AI model for this task. Model restrictions are applied based on environment configuration."
                }
                schema["required"].append("model")
            else:
                # Normal mode, model is optional with available options
                schema["properties"]["model"] = {
                    "type": "string",
                    "enum": available_models + [self.config.DEFAULT_MODEL],
                    "default": self.config.DEFAULT_MODEL,
                    "description": f"AI model to use. Available models (after restrictions): {', '.join(available_models)}. Defaults to '{self.config.DEFAULT_MODEL}'."
                }
        else:
            # No models available due to restrictions or missing API keys
            schema["properties"]["model"] = {
                "type": "string",
                "description": "No models available. Please check API keys and model restrictions in environment variables."
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
        
        Features:
        - Conversation continuation with thread management
        - Smart file deduplication across conversation turns
        - Model restriction enforcement
        - Multiple file handling modes (embedded/summary/reference)
        - Automatic directory expansion
        - Token limit management
        """
        try:
            # Validate request using Pydantic model
            request = SageRequest(**arguments)
            logger.info(f"SAGE {request.mode} mode called")
            
            # Check model restrictions
            if request.model and not self._is_model_allowed(request.model):
                available = self._get_available_models()
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Model '{request.model}' is not allowed. Available models: {', '.join(available)}"
                }))]
            
            # Validate file paths for security
            if request.files:
                valid, error = validate_paths(request.files)
                if not valid:
                    return [TextContent(type="text", text=json.dumps({
                        "error": f"Invalid file paths: {error}"
                    }))]
            
            # Handle conversation continuation
            conversation_context = None
            embedded_files = []
            if request.continuation_id:
                conversation_context = get_thread(request.continuation_id)
                if conversation_context:
                    # Get files already embedded in conversation
                    embedded_files = self._get_conversation_files(conversation_context)
                    logger.info(f"Continuing conversation {request.continuation_id} with {len(embedded_files)} embedded files")
                else:
                    logger.warning(f"Continuation ID {request.continuation_id} not found")
            
            # Smart file handling with deduplication
            file_contents = {}
            new_files = []
            if request.files:
                # Expand directories to individual files
                expanded_files = expand_paths(request.files)
                
                # Filter out files already in conversation history
                if embedded_files:
                    new_files = [f for f in expanded_files if f not in embedded_files]
                    logger.info(f"File deduplication: {len(expanded_files)} total, {len(new_files)} new, {len(embedded_files)} already embedded")
                else:
                    new_files = expanded_files
                
                # Read only new files
                if new_files:
                    file_contents = read_files(
                        new_files,
                        mode=request.file_handling_mode,
                        max_tokens=self._get_token_budget(request.model or self.config.DEFAULT_MODEL)
                    )
            
            # Auto-select model if needed
            model_name = request.model or self.config.DEFAULT_MODEL
            if model_name == "auto":
                model_name = select_best_model(
                    mode=request.mode,
                    prompt_size=len(request.prompt),
                    file_count=len(new_files),
                    conversation_context=conversation_context
                )
                logger.info(f"Auto-selected model: {model_name}")
            
            # Get provider and mode handler
            provider = get_provider(model_name)
            if not provider:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"No provider available for model: {model_name}"
                }))]
                
            handler = get_mode_handler(request.mode)
            if not handler:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Unknown mode: {request.mode}"
                }))]
            
            # Build comprehensive context
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
                "new_files": new_files
            }
            
            # Execute mode handler
            logger.info(f"Executing {request.mode} mode with {model_name}")
            result = await handler.handle(full_context, provider)
            
            # Handle conversation memory
            thread_id = request.continuation_id
            if not thread_id and len(result) > 100:  # Create new thread for substantial responses
                thread_id = create_thread(
                    tool_name="sage",
                    mode=request.mode,
                    initial_request=arguments
                )
                logger.info(f"Created new conversation thread: {thread_id}")
            
            if thread_id:
                # Add turn to conversation memory
                add_turn(
                    thread_id,
                    "user",
                    request.prompt,
                    files=new_files,  # Track only newly embedded files
                    tool_name="sage",
                    mode=request.mode
                )
                add_turn(
                    thread_id,
                    "assistant", 
                    result,
                    model_name=model_name
                )
                
                # Add continuation offer to response
                if not request.continuation_id:  # Only for new conversations
                    result += f"\n\n---\n💬 **Continue this conversation**: Use `continuation_id: {thread_id}` with any SAGE mode to continue this discussion with full context."
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            logger.error(f"Error in SAGE tool: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({
                "error": f"SAGE execution failed: {str(e)}"
            }))]
    
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