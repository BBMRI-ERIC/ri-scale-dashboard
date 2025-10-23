#!/bin/bash

echo "=========================================="
echo "RIScale DPSService Environment Setup"
echo "=========================================="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $SCRIPT_DIR"
ls

# Check if manifest file is provided as argument
MANIFEST_FILE="${1:-example_manifest.yaml}"

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: Manifest file '$MANIFEST_FILE' not found!"
    echo "Usage: $0 [manifest_file.yaml]"
    echo "Example: $0 example_manifest.yaml"
    exit 1
fi

echo "Using manifest: $MANIFEST_FILE"
echo ""

# Create temporary script for container execution
TEMP_SCRIPT="run_dps_service_temp.sh"

echo "Creating temporary script: $TEMP_SCRIPT"
echo ""

# Write the container execution script
echo "#!/bin/bash" > "$TEMP_SCRIPT"
echo "echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "echo \"Inside Container - Running DPSService\"" >> "$TEMP_SCRIPT"
echo "echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "hostname" >> "$TEMP_SCRIPT"
echo "cd /code" >> "$TEMP_SCRIPT"
echo "ls" >> "$TEMP_SCRIPT"
echo "" >> "$TEMP_SCRIPT"

# Navigate to RIScale directory inside container
echo "cd /code/RIScale" >> "$TEMP_SCRIPT"
echo "ls" >> "$TEMP_SCRIPT"
echo "echo \"----------------------------------------\"" >> "$TEMP_SCRIPT"
echo "echo \"Setting up Python environment\"" >> "$TEMP_SCRIPT"
echo "echo \"----------------------------------------\"" >> "$TEMP_SCRIPT"
echo "" >> "$TEMP_SCRIPT"

# Virtual environment setup
VENV_NAME="venv_riscale"
echo "echo \"Checking for virtual environment: $VENV_NAME\"" >> "$TEMP_SCRIPT"
echo "if [ -d \"$VENV_NAME\" ]; then" >> "$TEMP_SCRIPT"
echo "    echo \"Virtual environment '$VENV_NAME' exists, activating...\"" >> "$TEMP_SCRIPT"
echo "    source ./$VENV_NAME/bin/activate" >> "$TEMP_SCRIPT"
echo "else" >> "$TEMP_SCRIPT"
echo "    echo \"Creating virtual environment '$VENV_NAME'...\"" >> "$TEMP_SCRIPT"
echo "    python3 -m venv $VENV_NAME" >> "$TEMP_SCRIPT"
echo "    source ./$VENV_NAME/bin/activate" >> "$TEMP_SCRIPT"
echo "    echo \"Upgrading pip...\"" >> "$TEMP_SCRIPT"
echo "    python3 -m pip install --upgrade pip" >> "$TEMP_SCRIPT"
echo "    echo \"Installing PyYAML...\"" >> "$TEMP_SCRIPT"
echo "    python3 -m pip install pyyaml" >> "$TEMP_SCRIPT"
echo "    # Add additional packages as needed:" >> "$TEMP_SCRIPT"
echo "    # python3 -m pip install numpy pandas pillow" >> "$TEMP_SCRIPT"
echo "    # python3 -m pip install opencv-python" >> "$TEMP_SCRIPT"
echo "fi" >> "$TEMP_SCRIPT"
echo "" >> "$TEMP_SCRIPT"

# Display environment info
echo "echo \"\"" >> "$TEMP_SCRIPT"
echo "echo \"Python environment info:\"" >> "$TEMP_SCRIPT"
echo "which python3" >> "$TEMP_SCRIPT"
echo "python3 --version" >> "$TEMP_SCRIPT"
echo "echo \$VIRTUAL_ENV" >> "$TEMP_SCRIPT"
echo "echo \"\"" >> "$TEMP_SCRIPT"

# Run DPSService
echo "echo \"----------------------------------------\"" >> "$TEMP_SCRIPT"
echo "echo \"Running DPSService\"" >> "$TEMP_SCRIPT"
echo "echo \"----------------------------------------\"" >> "$TEMP_SCRIPT"
echo "python3 DPSService.py -m $MANIFEST_FILE -v" >> "$TEMP_SCRIPT"
echo "" >> "$TEMP_SCRIPT"
echo "if [ \$? -eq 0 ]; then" >> "$TEMP_SCRIPT"
echo "    echo \"\"" >> "$TEMP_SCRIPT"
echo "    echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "    echo \"DPSService completed successfully\"" >> "$TEMP_SCRIPT"
echo "    echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "else" >> "$TEMP_SCRIPT"
echo "    echo \"\"" >> "$TEMP_SCRIPT"
echo "    echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "    echo \"DPSService failed\"" >> "$TEMP_SCRIPT"
echo "    echo \"=========================================\"" >> "$TEMP_SCRIPT"
echo "    exit 1" >> "$TEMP_SCRIPT"
echo "fi" >> "$TEMP_SCRIPT"

# Make the temporary script executable
chmod +x "$TEMP_SCRIPT"

echo "Temporary script created and made executable"
echo ""
echo "----------------------------------------"
echo "Executing via run.sh"
echo "----------------------------------------"
echo ""

# Execute the script via run.sh (container/singularity execution)
./run.sh ./$TEMP_SCRIPT

# Capture exit code
EXIT_CODE=$?

# Clean up temporary script
echo ""
echo "Cleaning up temporary script..."
rm "$TEMP_SCRIPT"

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Processing completed successfully"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "Processing failed with exit code $EXIT_CODE"
    echo "=========================================="
    exit $EXIT_CODE
fi

exit 0
