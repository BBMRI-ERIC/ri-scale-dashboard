# Shared Configuration

This directory contains configuration files shared between the frontend and backend to ensure consistency and prevent mismatches.

## Step Types Configuration

**File:** `step_types_config.yaml`

This YAML file is the **single source of truth** for all DPS pipeline step type definitions. Both the frontend GUI and backend service load this file to ensure they stay in sync.

### Structure

The configuration defines:
- **Step types:** load, custom_command, join
- **Parameters:** Each step type's configurable parameters
- **Validation rules:** Required fields, patterns, defaults
- **UI metadata:** Labels, help text, icons, examples

### Usage

#### Backend (Python)
```python
from dps_service.step_types_config import (
    load_step_types_config,
    get_step_type_config,
    validate_step_params
)

# Load the full config
config = load_step_types_config()

# Get config for a specific step type
load_config = get_step_type_config('load')

# Validate step parameters
is_valid, errors = validate_step_params('load', {
    'output_source_name': 'my_source',
    'mode': 'discovery',
    'path': './data'
})
```

#### Frontend (JavaScript/Vue)
```javascript
import { 
  STEP_TYPES_CONFIG,
  getStepTypeConfig,
  isParamRequired 
} from '@/configs/step_types_config.js'

// Access the config (camelCase keys)
const config = STEP_TYPES_CONFIG

// Get config for a step type
const loadConfig = getStepTypeConfig('load')

// Check if parameter is required
const isRequired = isParamRequired('load', 'output_source_name', formState)
```

### Maintaining the Config

**Important:** When adding or modifying step types:

1. ✅ **DO** edit only `configs/step_types_config.yaml`
2. ❌ **DON'T** edit frontend or backend code directly for config changes
3. ✅ **DO** test changes in both frontend and backend
4. ✅ **DO** keep documentation in sync (dps_service/Readme.md)

### Key Benefits

- **Single Source of Truth:** No duplicate config files to keep in sync
- **Automatic Consistency:** Frontend and backend always use same definitions
- **Type Safety:** Parameter types, defaults, and validation rules are centralized
- **Easy Maintenance:** Change once, applies everywhere
- **Documentation:** Config file itself serves as API documentation

### File Locations

```
/configs/
  step_types_config.yaml       # Single source of truth (YAML)

/dps_service/
  step_types_config.py          # Python loader module

/frontend/src/configs/
  step_types_config.js          # JavaScript loader module
```

### Version History

- **v1.0** (2026-01-22): Initial shared config with load, custom_command, join step types
