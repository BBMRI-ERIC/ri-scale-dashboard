"""
Step Types Configuration Loader for DPS Service

This module loads the shared step_types_config.yaml file to ensure
frontend and backend use the same configuration, preventing mismatches.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


# Path to the shared config file (workspace root /configs)
_CONFIG_PATH = Path(__file__).resolve().parents[3] / 'configs' / 'step_types_config.yaml'


def load_step_types_config() -> Dict[str, Any]:
    """
    Load and parse the step types configuration YAML file.
    
    Returns:
        dict: Parsed configuration containing step type definitions
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the config file is invalid YAML
    """
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(f"Step types config not found at {_CONFIG_PATH}")
    
    with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_step_type_config(step_type: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific step type.
    
    Args:
        step_type: The step type name (e.g., 'load', 'custom_command', 'join')
        
    Returns:
        dict: Configuration for the step type, or None if not found
    """
    config = load_step_types_config()
    return config.get('step_types', {}).get(step_type)


def get_param_config(step_type: str, param_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific parameter of a step type.
    
    Args:
        step_type: The step type name
        param_name: The parameter name
        
    Returns:
        dict: Configuration for the parameter, or None if not found
    """
    type_config = get_step_type_config(step_type)
    if not type_config:
        return None
    
    return type_config.get('params', {}).get(param_name)


def get_param_default(step_type: str, param_name: str) -> Any:
    """
    Get the default value for a parameter.
    
    Args:
        step_type: The step type name
        param_name: The parameter name
        
    Returns:
        The default value for the parameter, or None if not specified
    """
    param_config = get_param_config(step_type, param_name)
    if not param_config:
        return None
    
    return param_config.get('default')


def is_param_required(step_type: str, param_name: str) -> bool:
    """
    Check if a parameter is always required.
    
    Note: This only checks for unconditionally required parameters.
    For conditionally required parameters (required_when), you'll need
    to evaluate the condition with the current form state.
    
    Args:
        step_type: The step type name
        param_name: The parameter name
        
    Returns:
        bool: True if the parameter is required
    """
    param_config = get_param_config(step_type, param_name)
    if not param_config:
        return False
    
    return param_config.get('required', False)


def validate_step_params(step_type: str, params: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate step parameters against the configuration.
    
    Args:
        step_type: The step type name
        params: Dictionary of parameter values
        
    Returns:
        tuple: (is_valid, error_messages)
            - is_valid: True if all validations pass
            - error_messages: List of validation error messages
    """
    errors = []
    type_config = get_step_type_config(step_type)
    
    if not type_config:
        return False, [f"Unknown step type: {step_type}"]
    
    param_configs = type_config.get('params', {})
    
    # Check required parameters
    for param_name, param_config in param_configs.items():
        if param_config.get('required', False):
            if param_name not in params or params[param_name] is None:
                label = param_config.get('label', param_name)
                errors.append(f"Missing required parameter: {label} ({param_name})")
        
        # Check conditionally required (simple implementation)
        required_when = param_config.get('required_when')
        if required_when and param_name not in params:
            # Parse simple conditions like "mode == 'discovery'"
            # This is a simplified implementation; extend as needed
            errors.append(f"Parameter {param_name} may be required depending on other values")
    
    # Validate patterns if specified
    for param_name, value in params.items():
        if param_name not in param_configs:
            continue
            
        param_config = param_configs[param_name]
        validation = param_config.get('validation', {})
        
        if 'pattern' in validation and value is not None:
            import re
            pattern = validation['pattern']
            if isinstance(value, str) and not re.match(pattern, value):
                error_msg = validation.get('error_message', f"Invalid format for {param_name}")
                errors.append(error_msg)
    
    return len(errors) == 0, errors


def get_all_step_types() -> list[str]:
    """
    Get list of all available step type names.
    
    Returns:
        list: List of step type names
    """
    config = load_step_types_config()
    return list(config.get('step_types', {}).keys())


def get_command_chains() -> Dict[str, Any]:
    """Return all composite command chains defined in the config."""
    config = load_step_types_config()
    return config.get('command_chains', {})


def get_command_chain(name: str) -> Optional[Dict[str, Any]]:
    """Return a specific composite command chain by name."""
    return get_command_chains().get(name)


# Cache the config for performance (reload only when needed)
_cached_config: Optional[Dict[str, Any]] = None


def get_cached_config() -> Dict[str, Any]:
    """
    Get cached configuration (loads on first call, then caches).
    
    Returns:
        dict: Cached configuration
    """
    global _cached_config
    if _cached_config is None:
        _cached_config = load_step_types_config()
    return _cached_config


if __name__ == '__main__':
    # Test the configuration loading
    print("Loading step types configuration...")
    config = load_step_types_config()
    print(f"Config version: {config.get('version')}")
    print(f"Available step types: {get_all_step_types()}")
    
    # Test getting a specific step config
    print("\n--- Load Step Config ---")
    load_config = get_step_type_config('load')
    if load_config:
        print(f"Display name: {load_config.get('display_name')}")
        print(f"Backend type: {load_config.get('backend_type')}")
        print(f"Number of params: {len(load_config.get('params', {}))}")
    
    # Test parameter validation
    print("\n--- Parameter Validation Test ---")
    test_params = {
        'output_source_name': 'test_source',
        'mode': 'discovery',
        'path': './data',
    }
    is_valid, errors = validate_step_params('load', test_params)
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
