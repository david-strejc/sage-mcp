# Output File Parameter Design

## Summary

Add `output_file` parameter to the SAGE tool that saves output directly to a file instead of returning large content in the response.

## Problem

When SAGE generates large outputs (code analysis, reviews, etc.), returning the full content:
- Consumes context tokens unnecessarily
- Floods the conversation with large text blocks
- Makes it harder to process results programmatically

## Solution

Add optional `output_file` parameter to the sage tool:

```python
output_file: Optional[str] = Field(
    default=None,
    description="Save output directly to this file path instead of returning content."
)
```

## Behavior

1. When `output_file` is NOT set: Current behavior (return full content)
2. When `output_file` IS set:
   - Validate path security using existing `validate_paths()`
   - Execute normally to get result
   - Write result to specified file
   - Return confirmation: `"Output saved to {path} ({human_readable_size})"`

## Implementation Changes

### `tools/sage.py`

1. Add `output_file` field to `SageRequest` model
2. Add `output_file` to `get_input_schema()` properties
3. Modify `execute()` to check for output_file and write instead of return

### Files Modified

- `tools/sage.py` - Add parameter and file writing logic

## Security

- Reuse existing `validate_paths()` for path validation
- Prevent writes outside allowed directories
- Check for path traversal attacks
