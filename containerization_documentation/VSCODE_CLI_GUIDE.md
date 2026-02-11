# VS Code CLI in RI-SCALE Container

The RI-SCALE Dashboard containers now include the **VS Code CLI** for remote development and code editing.

## What is VS Code CLI?

The VS Code CLI (`code`) is a lightweight command-line interface that allows you to:
- Use VS Code from the terminal
- Start VS Code Server (web-based VS Code)
- Create code tunnels for secure remote access
- Edit files and run commands remotely

## Quick Start

### Check VS Code CLI Version

```bash
# Apptainer
apptainer exec ri-scale-dashboard.sif code --version

# Docker
docker exec ri-scale-dashboard code --version
```

### Start VS Code Server (Web Browser)

Run VS Code in server mode to access it through your browser:

```bash
# Apptainer
apptainer exec ri-scale-dashboard.sif code serve-web \
  --accept-server-license-terms \
  --bind 0.0.0.0:8443
```

Then open: **https://localhost:8443**

### Create a Code Tunnel

For secure remote access from anywhere:

```bash
# Apptainer
apptainer exec ri-scale-dashboard.sif code tunnel \
  --accept-server-license-terms
```

This creates a secure tunnel and provides you with a URL to access VS Code remotely.

### Open a Folder in VS Code

```bash
# Apptainer
apptainer exec ri-scale-dashboard.sif code /opt/ri-scale
```

## Common VS Code CLI Commands

| Command | Purpose |
|---------|---------|
| `code --version` | Show VS Code version |
| `code --list-extensions` | List installed extensions |
| `code --install-extension <id>` | Install extension |
| `code <path>` | Open file/folder |
| `code --new-window` | Create new window |
| `code serve-web` | Start web server |
| `code tunnel` | Create secure tunnel |
| `code --help` | Show all options |

## Full Examples

### Example 1: Apptainer with VS Code Web Server

**Terminal 1 - Start Backend:**
```bash
cd /home/wilfried/Documents/ri-scale-dashboard
./apptainer.sh backend
```

**Terminal 2 - Start VS Code Server:**
```bash
apptainer exec ri-scale-dashboard.sif code serve-web \
  --accept-server-license-terms \
  --bind 0.0.0.0:8443
```

**Then access:**
- VS Code: https://localhost:8443
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Example 2: Docker with VS Code Server

```bash
# Start container
docker-compose up -d

# Start VS Code server
docker exec ri-scale-dashboard code serve-web \
  --accept-server-license-terms \
  --bind 0.0.0.0:8443
```

**Access:**
- VS Code: https://localhost:8443
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173

### Example 3: HPC Remote Development

Create a SLURM job that starts VS Code server:

```bash
#!/bin/bash
#SBATCH --job-name=ri-scale-vscode
#SBATCH --partition=gpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00

module load apptainer

CONTAINER=/path/to/ri-scale-dashboard.sif

echo "Starting VS Code server..."
echo "Tunnel URL will appear below:"
echo

apptainer exec $CONTAINER code tunnel \
  --accept-server-license-terms
```

Submit with:
```bash
sbatch slurm-vscode.slurm
```

## Advanced Usage

### Install Extensions in Container

```bash
# Python extension
apptainer exec ri-scale-dashboard.sif code \
  --install-extension ms-python.python

# Pylance (Python language server)
apptainer exec ri-scale-dashboard.sif code \
  --install-extension ms-python.vscode-pylance

# Vue extension
apptainer exec ri-scale-dashboard.sif code \
  --install-extension vuetify.vs-code-vuetify
```

### Environment Variables

```bash
# Set VS Code settings
export VSCODE_CLI_HOME=/opt/vscode-cli
export VS_CODE_PORT=8443

apptainer exec ri-scale-dashboard.sif code serve-web
```

### Port Binding Options

```bash
# Bind to specific port and interface
code serve-web \
  --accept-server-license-terms \
  --bind 127.0.0.1:8443         # Local only
  
# Or accessible from network
code serve-web \
  --accept-server-license-terms \
  --bind 0.0.0.0:8443           # Any interface
```

## Troubleshooting

### Port Already in Use

```bash
# Use different port
apptainer exec ri-scale-dashboard.sif code serve-web \
  --accept-server-license-terms \
  --bind 0.0.0.0:9443
```

### VS Code Won't Start

```bash
# Check VS Code is installed
apptainer exec ri-scale-dashboard.sif which code

# Verify version
apptainer exec ri-scale-dashboard.sif code --version

# Check help
apptainer exec ri-scale-dashboard.sif code --help
```

### SSL/HTTPS Certificate Warning

This is normal for VS Code Server. The certificate is self-signed for the first run. You can:
1. Accept the warning and proceed
2. Use HTTP instead: `--no-secure` flag (not recommended for production)

### Tunnel Issues

```bash
# Reset tunnel
apptainer exec ri-scale-dashboard.sif code tunnel --renew-token

# Check tunnel status
apptainer exec ri-scale-dashboard.sif code tunnel --show-log
```

## Integration with Container Helper Script

You can add VS Code commands to the `apptainer.sh` helper script:

```bash
# Edit apptainer.sh and add:

vscode)
    apptainer exec ri-scale-dashboard.sif code serve-web \
        --accept-server-license-terms \
        --bind 0.0.0.0:8443
    ;;

vscode-tunnel)
    apptainer exec ri-scale-dashboard.sif code tunnel \
        --accept-server-license-terms
    ;;
```

Then use:
```bash
./apptainer.sh vscode        # Start web server
./apptainer.sh vscode-tunnel # Start tunnel
```

## Browser Compatibility

VS Code Server works best in:
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Performance Tips

1. **Use local VS Code Server** - Faster than tunnel
2. **Bind to localhost only** - Better security
3. **Use 8443 (default)** - Avoids port conflicts
4. **Keep VS Code CLI updated** - Check releases periodically

## Additional Resources

- [VS Code CLI Documentation](https://code.visualstudio.com/docs/editor/command-line)
- [VS Code Server](https://code.visualstudio.com/docs/remote/vscode-server)
- [VS Code Tunnels](https://code.visualstudio.com/docs/remote/tunnels)

## Location in Container

- **Executable**: `/opt/vscode-cli/code` or `/usr/local/bin/code`
- **Home**: `/opt/vscode-cli`
- **Extensions**: `/root/.vscode/extensions` (or `$HOME/.vscode/extensions`)

---

**Next Steps:**
1. Build container with VS Code CLI: `./apptainer.sh build`
2. Start VS Code server: `apptainer exec ri-scale-dashboard.sif code serve-web --accept-server-license-terms --bind 0.0.0.0:8443`
3. Open browser: https://localhost:8443
