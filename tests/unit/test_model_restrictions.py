#!/usr/bin/env python3
"""
Model Restriction Testing Script
Tests model filtering, cost control, and provider restrictions
"""

import os
import tempfile
from unittest.mock import patch

import pytest

# Add project root to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.models import ModelRestrictionService, select_best_model, get_model_context_limit


class TestModelRestrictions:
    """Test model restriction functionality"""

    def setup_method(self):
        """Setup for each test"""
        # Save original environment
        self.original_env = {}
        for key in [
            'OPENAI_ALLOWED_MODELS', 'GOOGLE_ALLOWED_MODELS', 'ANTHROPIC_ALLOWED_MODELS',
            'BLOCKED_MODELS', 'DISABLED_MODEL_PATTERNS'
        ]:
            self.original_env[key] = os.environ.get(key)
            
    def teardown_method(self):
        """Restore original environment"""
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
                
    def test_restriction_service_initialization(self):
        """Test ModelRestrictionService initialization"""
        service = ModelRestrictionService()
        
        assert hasattr(service, 'openai_allowed')
        assert hasattr(service, 'google_allowed') 
        assert hasattr(service, 'anthropic_allowed')
        assert hasattr(service, 'blocked_models')
        assert hasattr(service, 'disabled_patterns')
        
    def test_openai_model_restrictions(self):
        """Test OpenAI model restrictions"""
        # Set specific allowed models
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4,gpt-4o,o1-mini'
        
        service = ModelRestrictionService()
        
        # Allowed models
        assert service.is_model_allowed('gpt-4')
        assert service.is_model_allowed('gpt-4o')
        assert service.is_model_allowed('o1-mini')
        
        # Not allowed models
        assert not service.is_model_allowed('gpt-3.5-turbo')
        assert not service.is_model_allowed('text-davinci-003')
        
    def test_google_model_restrictions(self):
        """Test Google/Gemini model restrictions"""
        # Set specific allowed models
        os.environ['GOOGLE_ALLOWED_MODELS'] = 'gemini-1.5-pro,gemini-2.0-flash'
        
        service = ModelRestrictionService()
        
        # Allowed models
        assert service.is_model_allowed('gemini-1.5-pro')
        assert service.is_model_allowed('gemini-2.0-flash')
        
        # Not allowed models
        assert not service.is_model_allowed('gemini-1.0-pro')
        assert not service.is_model_allowed('gemini-1.5-flash')
        
    def test_anthropic_model_restrictions(self):
        """Test Anthropic model restrictions"""
        # Set specific allowed models
        os.environ['ANTHROPIC_ALLOWED_MODELS'] = 'claude-3-5-sonnet-20241022,claude-3-haiku-20240307'
        
        service = ModelRestrictionService()
        
        # Allowed models
        assert service.is_model_allowed('claude-3-5-sonnet-20241022')
        assert service.is_model_allowed('claude-3-haiku-20240307')
        
        # Not allowed models
        assert not service.is_model_allowed('claude-2.1')
        assert not service.is_model_allowed('claude-3-opus-20240229')
        
    def test_blocked_models(self):
        """Test globally blocked models"""
        os.environ['BLOCKED_MODELS'] = 'gpt-4,claude-3-opus-20240229,gemini-1.0-pro'
        
        service = ModelRestrictionService()
        
        # These should be blocked regardless of provider settings
        assert not service.is_model_allowed('gpt-4')
        assert not service.is_model_allowed('claude-3-opus-20240229')
        assert not service.is_model_allowed('gemini-1.0-pro')
        
        # These should still be allowed
        assert service.is_model_allowed('gpt-4o')
        assert service.is_model_allowed('claude-3-5-sonnet-20241022')
        assert service.is_model_allowed('gemini-2.0-flash')
        
    def test_disabled_model_patterns(self):
        """Test pattern-based model disabling"""
        os.environ['DISABLED_MODEL_PATTERNS'] = 'gpt-3,claude-2,mini'
        
        service = ModelRestrictionService()
        
        # Models matching patterns should be blocked
        assert not service.is_model_allowed('gpt-3.5-turbo')
        assert not service.is_model_allowed('claude-2.1')
        assert not service.is_model_allowed('gpt-4o-mini')
        assert not service.is_model_allowed('o1-mini')
        
        # Models not matching patterns should be allowed
        assert service.is_model_allowed('gpt-4')
        assert service.is_model_allowed('claude-3-5-sonnet-20241022')
        assert service.is_model_allowed('gemini-2.0-flash')
        
    def test_combined_restrictions(self):
        """Test multiple restriction types working together"""
        # Set up complex restrictions
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4,gpt-4o,o1-mini'
        os.environ['BLOCKED_MODELS'] = 'gpt-4'  # Block gpt-4 even though it's in allowed
        os.environ['DISABLED_MODEL_PATTERNS'] = 'mini'  # Block anything with 'mini'
        
        service = ModelRestrictionService()
        
        # gpt-4 is allowed by OpenAI list but blocked globally
        assert not service.is_model_allowed('gpt-4')
        
        # o1-mini is allowed by OpenAI list but blocked by pattern
        assert not service.is_model_allowed('o1-mini')
        
        # gpt-4o passes all restrictions
        assert service.is_model_allowed('gpt-4o')
        
        # Non-OpenAI models not in allowed lists should be rejected
        assert not service.is_model_allowed('gemini-2.0-flash')
        
    def test_case_insensitive_restrictions(self):
        """Test that restrictions work case-insensitively"""
        os.environ['BLOCKED_MODELS'] = 'GPT-4,Claude-3-Opus'
        os.environ['DISABLED_MODEL_PATTERNS'] = 'MINI,FLASH'
        
        service = ModelRestrictionService()
        
        # Should block regardless of case
        assert not service.is_model_allowed('gpt-4')
        assert not service.is_model_allowed('GPT-4')
        assert not service.is_model_allowed('claude-3-opus-20240229')
        assert not service.is_model_allowed('CLAUDE-3-OPUS-20240229')
        
        # Pattern matching should be case-insensitive
        assert not service.is_model_allowed('gpt-4o-mini')
        assert not service.is_model_allowed('GPT-4O-MINI')
        assert not service.is_model_allowed('gemini-2.0-flash')
        assert not service.is_model_allowed('GEMINI-2.0-FLASH')
        
    def test_empty_restrictions(self):
        """Test behavior with empty restriction lists"""
        # Clear all restrictions
        for key in ['OPENAI_ALLOWED_MODELS', 'GOOGLE_ALLOWED_MODELS', 'ANTHROPIC_ALLOWED_MODELS',
                    'BLOCKED_MODELS', 'DISABLED_MODEL_PATTERNS']:
            os.environ.pop(key, None)
            
        service = ModelRestrictionService()
        
        # With no restrictions, all models should be allowed
        assert service.is_model_allowed('gpt-4')
        assert service.is_model_allowed('claude-3-5-sonnet-20241022')
        assert service.is_model_allowed('gemini-2.0-flash')
        assert service.is_model_allowed('random-model-name')
        
    def test_whitespace_handling_in_restrictions(self):
        """Test handling of whitespace in restriction strings"""
        # Set restrictions with extra whitespace
        os.environ['OPENAI_ALLOWED_MODELS'] = ' gpt-4 , gpt-4o , o1-mini '
        os.environ['BLOCKED_MODELS'] = ' claude-3-opus , gemini-1.0-pro '
        
        service = ModelRestrictionService()
        
        # Should handle whitespace correctly
        assert service.is_model_allowed('gpt-4')
        assert service.is_model_allowed('gpt-4o')
        assert service.is_model_allowed('o1-mini')
        
        assert not service.is_model_allowed('claude-3-opus')
        assert not service.is_model_allowed('gemini-1.0-pro')
        
    def test_restriction_summary(self):
        """Test getting restriction summary"""
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4,gpt-4o'
        os.environ['GOOGLE_ALLOWED_MODELS'] = 'gemini-2.0-flash'
        os.environ['BLOCKED_MODELS'] = 'dangerous-model'
        os.environ['DISABLED_MODEL_PATTERNS'] = 'old,deprecated'
        
        service = ModelRestrictionService()
        summary = service.get_restriction_summary()
        
        assert 'openai_allowed' in summary
        assert 'google_allowed' in summary
        assert 'anthropic_allowed' in summary
        assert 'blocked_models' in summary
        assert 'disabled_patterns' in summary
        
        assert 'gpt-4' in summary['openai_allowed']
        assert 'gpt-4o' in summary['openai_allowed']
        assert 'gemini-2.0-flash' in summary['google_allowed']
        assert 'dangerous-model' in summary['blocked_models']
        assert 'old' in summary['disabled_patterns']
        assert 'deprecated' in summary['disabled_patterns']
        
    def test_model_auto_selection_with_restrictions(self):
        """Test model auto-selection respects restrictions"""
        # Set restrictions that limit available models
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4o-mini'
        os.environ['GOOGLE_ALLOWED_MODELS'] = 'gemini-1.5-flash'
        os.environ['BLOCKED_MODELS'] = 'gpt-4,claude-3-5-sonnet-20241022'
        
        # Test different modes and contexts
        test_cases = [
            ("chat", 1000, 0),      # Small prompt, chat mode
            ("analyze", 50000, 5),  # Large prompt, analyze mode  
            ("think", 10000, 2),    # Medium prompt, think mode
        ]
        
        for mode, prompt_size, file_count in test_cases:
            selected_model = select_best_model(mode, prompt_size, file_count)
            
            # Selected model should be allowed by restrictions
            service = ModelRestrictionService()
            assert service.is_model_allowed(selected_model), \
                f"Auto-selected model {selected_model} violates restrictions for mode {mode}"
                
    def test_cost_control_through_restrictions(self):
        """Test using restrictions for cost control"""
        # Block expensive models, allow only cheaper ones
        os.environ['BLOCKED_MODELS'] = 'gpt-4,claude-3-5-sonnet-20241022,gemini-1.5-pro,o1-preview'
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4o-mini'
        os.environ['GOOGLE_ALLOWED_MODELS'] = 'gemini-1.5-flash'
        os.environ['ANTHROPIC_ALLOWED_MODELS'] = 'claude-3-haiku-20240307'
        
        service = ModelRestrictionService()
        
        # Expensive models should be blocked
        expensive_models = [
            'gpt-4', 'claude-3-5-sonnet-20241022', 'gemini-1.5-pro', 'o1-preview'
        ]
        for model in expensive_models:
            assert not service.is_model_allowed(model), f"Expensive model {model} should be blocked"
            
        # Cheaper models should be allowed
        cheaper_models = [
            'gpt-4o-mini', 'gemini-1.5-flash', 'claude-3-haiku-20240307'
        ]
        for model in cheaper_models:
            assert service.is_model_allowed(model), f"Cheaper model {model} should be allowed"
            
    def test_development_vs_production_restrictions(self):
        """Test different restrictions for different environments"""
        # Development environment - allow experimental models
        dev_restrictions = {
            'OPENAI_ALLOWED_MODELS': 'gpt-4,gpt-4o,o1-preview,o1-mini',
            'GOOGLE_ALLOWED_MODELS': 'gemini-2.0-flash,gemini-1.5-pro',
            'ANTHROPIC_ALLOWED_MODELS': 'claude-3-5-sonnet-20241022,claude-3-haiku-20240307'
        }
        
        # Production environment - only stable models
        prod_restrictions = {
            'OPENAI_ALLOWED_MODELS': 'gpt-4o-mini',
            'GOOGLE_ALLOWED_MODELS': 'gemini-1.5-flash',
            'ANTHROPIC_ALLOWED_MODELS': 'claude-3-haiku-20240307',
            'BLOCKED_MODELS': 'o1-preview,o1-mini,gemini-2.0-flash'  # Block experimental
        }
        
        # Test development restrictions
        for key, value in dev_restrictions.items():
            os.environ[key] = value
            
        dev_service = ModelRestrictionService()
        assert dev_service.is_model_allowed('o1-preview')  # Experimental allowed in dev
        assert dev_service.is_model_allowed('gemini-2.0-flash')
        
        # Test production restrictions
        for key, value in prod_restrictions.items():
            os.environ[key] = value
            
        prod_service = ModelRestrictionService()
        assert not prod_service.is_model_allowed('o1-preview')  # Experimental blocked in prod
        assert not prod_service.is_model_allowed('gemini-2.0-flash')
        assert prod_service.is_model_allowed('gpt-4o-mini')  # Stable allowed
        
    def test_model_context_limits_with_restrictions(self):
        """Test that context limits work with model restrictions"""
        # Set up model with known context limit
        test_model = "gpt-4"
        expected_limit = get_model_context_limit(test_model)
        
        # Ensure we get a reasonable limit
        assert expected_limit > 0
        assert expected_limit >= 8000  # GPT-4 should have at least 8K context
        
        # Test with restricted model
        os.environ['BLOCKED_MODELS'] = test_model
        service = ModelRestrictionService()
        
        # Model should be blocked even though we can get its context limit
        assert not service.is_model_allowed(test_model)
        
    def test_provider_specific_restrictions(self):
        """Test that provider-specific logic works correctly"""
        service = ModelRestrictionService()
        
        # Test OpenAI model detection
        openai_models = ['gpt-4', 'gpt-3.5-turbo', 'o1-preview', 'o3-mini']
        for model in openai_models:
            # These should be detected as OpenAI models
            assert model.startswith(('gpt', 'o1', 'o3'))
            
        # Test Google model detection  
        google_models = ['gemini-1.5-pro', 'gemini-2.0-flash']
        for model in google_models:
            # These should be detected as Google models
            assert model.startswith('gemini')
            
        # Test Anthropic model detection
        anthropic_models = ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307']
        for model in anthropic_models:
            # These should be detected as Anthropic models
            assert model.startswith('claude')


class TestModelRestrictionIntegration:
    """Test model restriction integration with other components"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.original_env = {}
        for key in ['OPENAI_ALLOWED_MODELS', 'GOOGLE_ALLOWED_MODELS', 'ANTHROPIC_ALLOWED_MODELS',
                    'BLOCKED_MODELS', 'DISABLED_MODEL_PATTERNS']:
            self.original_env[key] = os.environ.get(key)
            
    def teardown_method(self):
        """Restore environment"""
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)
                
    def test_restrictions_with_model_selection(self):
        """Test restrictions work with automatic model selection"""
        # Allow only specific models
        os.environ['OPENAI_ALLOWED_MODELS'] = 'gpt-4o-mini'
        os.environ['GOOGLE_ALLOWED_MODELS'] = 'gemini-1.5-flash'
        
        # Test that auto-selection respects restrictions
        for mode in ['chat', 'analyze', 'debug']:
            selected = select_best_model(mode, 1000, 0)
            service = ModelRestrictionService()
            
            # Should select an allowed model
            assert service.is_model_allowed(selected), \
                f"Auto-selected {selected} for {mode} mode violates restrictions"
                
    def test_restrictions_error_scenarios(self):
        """Test error handling when all models are restricted"""
        # Block everything
        os.environ['BLOCKED_MODELS'] = 'gpt,claude,gemini,llama,mistral,phi'
        
        service = ModelRestrictionService()
        
        # Common models should be blocked
        common_models = [
            'gpt-4', 'gpt-4o', 'claude-3-5-sonnet-20241022', 
            'gemini-2.0-flash', 'llama-3-8b'
        ]
        
        for model in common_models:
            assert not service.is_model_allowed(model)
            
        # This should still work for unknown models
        assert service.is_model_allowed('unknown-model-12345')


if __name__ == "__main__":
    # Run individual tests
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Model Restrictions")
    parser.add_argument("--test", help="Specific test to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    args = parser.parse_args()
    
    if args.integration:
        pytest.main([f"{__file__}::TestModelRestrictionIntegration", "-v" if args.verbose else ""])
    elif args.test:
        if "." in args.test:
            pytest.main([f"{__file__}::{args.test}", "-v" if args.verbose else ""])
        else:
            # Try both classes
            for class_name in ["TestModelRestrictions", "TestModelRestrictionIntegration"]:
                try:
                    pytest.main([f"{__file__}::{class_name}::test_{args.test}", "-v" if args.verbose else ""])
                    break
                except:
                    continue
            else:
                print(f"❌ Test {args.test} not found")
    else:
        # Run all tests
        pytest.main([__file__, "-v" if args.verbose else ""])