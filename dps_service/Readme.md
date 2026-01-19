
# RIScale - Data Preparation for Exploitation Service (DPS)

# Overview

The Data Preparation for Exploitation Service (DPS) is a user-invoked service that prepares datasets for downstream use. It translates heterogeneous data inputs into standardized formats suitable for algorithmic processing, while maintaining consistent metadata and directory structure conventions across the platform.

# Manifest File

The manifest file is a YAML configuration that defines the data preparation pipeline. It specifies data sources to load, processing steps to execute, and how to handle data transformations.

## Running the DPS with a Manifest

```bash
python dps_service.py -m ./path/to/manifest.yaml -v
```

- `-m` or `--manifest`: Path to the manifest YAML file (required)
- `-v` or `--verbose`: Enable verbose logging output (optional)

---

## Manifest Structure

### Top-Level Metadata Fields

#### `manifest_id` (string)
Unique identifier for this manifest configuration. Used for tracking and logging.

**Example:**
```yaml
manifest_id: "id2025-11-13"
```

#### `created_by` (string)
Email or username of the person who created this manifest.

**Example:**
```yaml
created_by: "user@example.org"
```

#### `created_at` (string)
ISO 8601 formatted timestamp indicating when the manifest was created.

**Example:**
```yaml
created_at: "2025-11-13T10:00:00Z"
```

#### `simulated` (boolean)
Controls execution mode:
- `true` (default): Runs in simulation mode - commands are logged but not executed
- `false`: Runs in production mode - actually executes all steps

**Example:**
```yaml
simulated: true
```

---

## Job Steps

The `job_steps` section is a list of sequential data preparation steps to execute. Each step has a specific type that determines its behavior.

### Common Step Properties

All steps have these properties:

- **step_name** (string): Descriptive name for the step (used in logging)
- **type** (string): The type of step to execute
- **enabled** (boolean): Whether to execute this step (default: `true`)
- **params** (object): Step-specific configuration parameters

---

## Step Types and Parameters

### 1. Load (`type: load`)

Loads data from files or directories into a named source that can be used by subsequent steps.

#### Load Mode: `discovery`

Discovers files matching a pattern and extracts metadata from filenames using regex.

**Parameters:**
- **output_source_name** (string, required): Name to register this data source
- **mode** (string, required): Set to `"discovery"`
- **path** (string, required): Directory path to search for files
- **include** (string, required): File pattern to match (e.g., `"*.svs"`, `"*.dcm"`)
- **recursive** (boolean, default: `false`): Search recursively in subdirectories
- **directory_mode** (boolean, default: `false`): If `true`, treats directories as data items instead of files.
- **columns** (object, required for discovery):
  - **column_name** (string): The column name to store file/directory paths
  - **filename_to_columnname** (string): Regex pattern to extract metadata from filename. Named capture groups become column names. Example: `"^(?P<slide_id>.+?)(?=\\.svs$)"` extracts the slide ID from a `.svs` filename
- **file_type** (string, optional): Specifies the data loader to be used for lazy loading. This is not commonly used, but can be helpful if more specialized steps need to be implemented inside the python framework. Loaders will load the data pointed to by the path. Currently, there are only some exampe loaders, such as **csv** for csv-files. New loaders can be added using the **@register annotation** of the `dpsdataset/loaders` submodule.

**Example:**
```yaml
- step_name: load svs data
  type: load
  enabled: true
  params:
    output_source_name: svs_source
    mode: "discovery"
    path: "./data"
    include: "*.svs"
    recursive: false
    directory_mode: false
    columns:
      column_name: "svs_path"
      filename_to_columnname: "^(?P<slide_id>.+?)(?=\\.svs$)"
```

**Result:** Creates a DataFrame with columns:
- `svs_path`: Full path to each discovered file
- `slide_id`: Extracted from filename via regex

---

#### Load Mode: `csv_file`

Loads data from a CSV file directly.

**Parameters:**
- **output_source_name** (string, required): Name to register this data source
- **mode** (string, required): Set to `"csv_file"`
- **path** (string, required): Path to the CSV file
- **columns** (object, optional):
  - **header** (boolean, default: `true`): Whether the CSV has a header row
  - **delimiter** (string, default: `",")`): Field delimiter character

**Example:**
```yaml
- step_name: load labels csv data
  type: load
  enabled: true
  params:
    output_source_name: labels_source
    mode: "csv_file"
    path: "./data/labels.csv"
    columns:
      header: true
      delimiter: ","
```

---

### 2. Custom Command (`type: custom_command`)

Executes shell commands, either once or once per row of input data.

**Parameters:**
- **command** (string, required): Shell command to execute. Can include placeholders like `{column_name}` which will be substituted with row values
- **execution_mode** (string, default: `"per_row")`):
  - `"per_row"`: Execute the command once for each row in the input source, substituting placeholders with row values.
  - `"once"`: Execute the command a single time without row-based substitution
- **input_source_name** (string, conditional): Name of the input source to iterate over. Required when `execution_mode` is `"per_row"`

**Example (execute once):**
```yaml
- step_name: delete existing output folder
  type: custom_command
  enabled: true
  params:
    execution_mode: "once"
    command: "rm -rf ./data/output"
```

**Example (per row with placeholders):**
```yaml
- step_name: convert svs to dicom
  type: custom_command
  enabled: true
  params:
    input_source_name: svs_source
    execution_mode: "per_row"
    command: "wsidicomizer -i {wsi_path} -o ./data/dicom/{slide_id} --source opentile"
```

In the per-row example, `{svs_path}` and `{slide_id}` are replaced with values from each row of `source1`. These correspond to columns in the source's DataFrame.

---

### 3. Join (`type: join`)

Merges two data sources (DataFrames) based on matching key columns.

**Parameters:**
- **left_source_name** (string, required): Name of the left source to join
- **right_source_name** (string, required): Name of the right source to join
- **output_source_name** (string, required): Name to register the joined result
- **left_key** (string, required): Column name in the left source to join on
- **right_key** (string, required): Column name in the right source to join on
- **join_type** (string, default: `"inner"`): Type of join to perform:
  - `"inner"`: Keep only rows with matching keys in both sources
  - `"left"`: Keep all rows from left source, match right where possible
  - `"right"`: Keep all rows from right source, match left where possible
  - `"outer"`: Keep all rows from both sources
- **missing_policy** (string, default: `"drop"`): How to handle mismatched rows (currently only `"drop"` is implemented)

**Example:**
```yaml
- step_name: join results
  type: join
  enabled: true
  params:
    left_source_name: svs_source
    right_source_name: labels_source
    output_source_name: labels_and_data_source
    left_key: slide_id
    right_key: slide_id
    join_type: inner
    missing_policy: drop
```

---

## Complete Example Workflow

The `example_manifest.yaml` demonstrates a complete workflow for svs loading and dicom conversion:

1. **Load WSI files** → Discover `.svs` files and extract slide IDs
2. **Load labels** → Load CSV file with metadata
3. **Setup** → Create output directory (once)
4. **Convert** → Run wsidicomizer on each WSI file (per row)
5. **Load DICOM output** → Discover generated DICOM directories
6. **Join results** → Combine WSI metadata with labels
7. **Join DICOM** → Add DICOM paths to the final result

Each step's output becomes available as a named source for subsequent steps.

---

## Data Flow

Data flows through the pipeline as follows:

1. **Load Steps**: Create Sources (named data collections)
2. **Processing Steps** (custom commands): Transform or generate new data
3. **Join Steps**: Combine multiple sources into unified datasets


Sources are referenced by name and can be used as input to custom commands or joins.

---

## Best Practices

1. **Use descriptive source names** that indicate the data they contain
2. **Test in simulated mode** (`simulated: true`) before running in production. This will also help you find some errors.
3. **Use regex groups** in discovery patterns to extract meaningful metadata like IDs
4. **Verify join keys** exist in both sources before performing joins
5. **Document custom commands** with clear step names explaining their purpose

---

# Framework Architecture

## Core Components

The DPS is built on a modular, pipeline-based architecture with the following key components:

### 1. **DPS Service** (`dps_service.py`)

The main entry point and orchestrator of the system. It:
- Parses YAML manifest files
- Initializes data sources based on the manifest
- Instantiates appropriate step processors based on step type
- Manages the overall pipeline execution
- Handles logging and error reporting

### 2. **DPS Pipeline** (`dps_pipeline.py`)

Represents a sequence of data preparation steps to be executed. It:
- Maintains a list of steps (`DPSStep` objects)
- Provides methods to add steps (`add_step()`, `add_steps()`)
- Executes steps one at a time using `run_next_step()`
- Tracks pipeline state and step count

### 3. **Data Sources** (`dpsdataset/source.py`)

Encapsulates data collections that flow through the pipeline:
- **Source**: A named data collection with a strategy for loading/retrieving data
- **Data Loading Strategies**: Different strategies for loading data:
  - **FileDiscoveryStrategy**: Discovers files matching a pattern, extracts metadata via regex, and creates a DataFrame with file paths and extracted columns
  - **CSVFileStrategy**: Loads data directly from CSV files with configurable headers and delimiters
  - **None**: Used for intermediate sources
- Sources can be registered by name and passed between steps
- Data can be lazily loaded on demand via `get_data()`

### 4. **Steps** (`step/`)

Steps are processing units that implement the `DPSStep` base class. Each step type performs a specific function:

#### **LoadStep** (implicit via `type: load`)
- Creates a new Source from a file discovery or CSV load operation
- Makes the data available for subsequent steps by registering it in the sources dictionary

#### **CustomCommandStep** (`step/custom_command.py`)
- Executes arbitrary shell commands
- Supports two execution modes:
  - **`once`**: Executes the command a single time
  - **`per_row`**: Iterates through rows in a source and executes the command for each row, substituting field placeholders (e.g., `{slide_id}`)
- Fields to substitute are automatically extracted from command text using regex
- Respects the simulated/production mode setting

#### **JoinStep** (`step/join.py`)
- Merges two Sources based on matching key columns
- Supports multiple join types: `inner`, `left`, `right`, `outer`
- Creates a new output Source with the merged data
- Uses pandas DataFrame merge operations internally

#### **ExampleDPSStep** (`step/example_dps_step.py`)
- A reference implementation demonstrating how to create custom DPS steps
- Can be used as a template for implementing domain-specific processing steps

### 5. **Data Loaders** (`dpsdataset/loaders.py`)

A registry system for data loaders that handle different file formats:
- Uses a `@register` decorator to register new loaders
- Loaders can lazily load data on demand
- Currently includes CSV loader as an example
- Extensible for additional file types (DICOM, images, etc.)

### Example: Registering a Custom Data Loader

Here's how to register a custom data loader for a new file format which can then be used for lazy loading:

```python
from dpsdataset.loaders import register
import json

@register("json")
def load(path):
    with open(self.path, 'r') as f:
        return json.load(f)
```

You can then use this loader in your manifest by specifying `file_type: "json"` in a load step. The registered loader will be automatically instantiated when data needs to be loaded.


### 6. **Lazy Dataframe** (`dpsdataset/lazy_dataframe`)
A wrapper around pandas DataFrames that enables lazy loading and memory-efficient data access. It defers data materialization until explicitly requested via `get_data()`, allowing the pipeline to work with large datasets without loading everything into memory upfront. Supports row-level iteration and column access while maintaining compatibility with the standard DataFrame interface. Lazy loading mechanics are implemented, but will only be needed if extending the framework with new steps that work with the data directly. There might still be some issues here as this quality of dev-life feature is WIP.


---

## Data Flow Architecture

```
┌─────────────────────┐
│  Parse Manifest     │
│   (YAML file)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Initialize Sources & Steps             │
│  - Create Source objects                │
│  - Instantiate Steps                    │
│  - Register sources by name             │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  Execute Pipeline (Sequential)          │
│  - Run each step one at a time          │
│  - Steps can read from registered       │
│    sources and write to new sources     |
|    or the file system                   │
│  - Sources remain available for         │
│    subsequent steps                     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  Final Output       │
│  (Named Source)     │
└─────────────────────┘
```


## Key Design Patterns

### **Registry Pattern**
Sources are registered by name in a dictionary, allowing steps to reference them by name without tight coupling. This enables:
- Flexible step ordering
- Easy composition of complex pipelines
- Clear data dependencies through naming

### **Strategy Pattern**
Data loading uses different strategies (`FileDiscoveryStrategy`, `CSVFileStrategy`) without changing the Source interface. This:
- Makes it easy to add new data source types
- Keeps code modular and testable
- Allows users to specify loading behavior in the manifest

### **Lazy Loading**
Data is not loaded until needed via `get_data()`. This:
- Improves memory efficiency for large datasets
- Allows pipelined processing
- Enables simulated execution without actual file I/O

### **Simulated vs Production Mode**
All steps respect a `simulated` flag that:
- In simulated mode: logs actions without executing actual commands
- In production mode: executes all steps normally
- Allows safe testing before running on real data

### **Command Pattern**
Each `DPSStep` encapsulates a request to perform a specific operation (load, transform, join, or execute a command) as an object.
The manifest defines steps declaratively, and the pipeline treats each step as a command object that can be passed around, stored and executed on demand without the caller knowing the specific implementation details.


---
