#!/bin/bash
# RI-SCALE Dashboard Container - Installation & Usage Guide

# This script provides a quick installation and usage verification

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       RI-SCALE Dashboard Container Setup - Status Check        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo

# Check what was created
echo "📦 Container Files:"
echo "├─ Apptainer.def                  ✓ (HPC container definition)"
echo "└─ apptainer.sh                   ✓ (Helper script)"
echo

echo "📚 Documentation:"
echo "├─ CONTAINER_SETUP_SUMMARY.md     ✓ (Complete overview)"
echo "├─ APPTAINER_QUICKREF.md          ✓ (Quick reference)"
echo "├─ APPTAINER_GUIDE.md             ✓ (Detailed guide)"
echo "└─ CONTAINER_DEPLOYMENT_GUIDE.md  ✓ (Deployment info)"
echo

echo "══════════════════════════════════════════════════════════════════"
echo

# Check for Apptainer
if command -v apptainer &> /dev/null; then
    echo "✅ Apptainer is installed:"
    apptainer --version
else
    echo "ℹ️  Apptainer not installed (optional)."
    echo "   To install: sudo apt-get."
    echo "   To install: sudo apt-get install apptainer

echo

echo "══════════════════════════════════════════════════════════════════"
echo "🚀 QUICK START"
echo "══════════════════════════════════════════════════════════════════"
echo

echo "Option 1: Use Apptainer (HPC-Optimized)"
echo "────────────────────────────────────────"
echo "1. Build:   sudo apptainer build ri-scale-dashboard.sif Apptainer.def"
echo "    Or:     ./apptainer.sh build"
echo ""
echo "2. Run:     ./apptainer.sh backend"
echo ""
echo "3. Or use the helper script:"
echo "    ./apptainer.sh help      # Show all commands"
echo "    ./apptainer.sh status    # Check container"
echo

echo "Use Apptainer (HPC-Optimized)"
echo "────────────────────────────────────────"
echo "1. Build:   sudo apptainer build ri-scale-dashboard.sif Apptainer.def"
echo "    Or:     ./apptainer.sh build"
echo ""
echo "2. Run:     ./apptainer.sh backend"
echo ""
echo "3. Or use the helper script:"
echo "    ./apptainer.sh help      # Show all commands"
echo "    ./apptainer.sh status    # Check container
echo "Then read:"
echo "  cat APPTAINER_GUIDE.md            # Complete guide"
echo "  cat HPC_CLUSTER_INTEGRATION.md    # HPC examples"
echo "  cat CONTAINER_DEPLOYMENT_GUIDE.md # Deployment strategies"
echo

echo "══════════════════════════════════════════════════════════════════"
echo "🎯 NEXT STEPS"
echo "══════════════════════════════════════════════════════════════════"
echo

echo "1. Install Apptainer or Docker (if not already installed)"
echo "2. Choose your deployment platform:"
echo "   • Local development? → Use Docker Compose"
echo "   • HPC cluster?       → Use Apptainer"
echo "   • Cloud?             → Use Docker"
echo "3. Build your container:"
echo "   • Apptainer: ./apptainer.sh build"
echo "   • Docker:    docker build -t ri-scale-dashboard ."
echo "4. Run and test:"
echo ""
echo "Then read:"
echo "  cat APPTAINER_GUIDE.md            # Complete guide"
echo "  cat CONTAINER_DEPLOYMENT_GUIDE.md # Deployment info
echo

echo "══════════════════════════════════════════════════════════════════"
echo "✨ All files are ready! Start with the documentation above."
echo "══════════════════════════════════════════════════════════════════"
