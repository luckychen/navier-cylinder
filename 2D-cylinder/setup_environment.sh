#!/bin/bash

# ============================================================================
# Setup Script for 2D Cylinder Flow Navier-Stokes Solver
# This script sets up the conda environment and builds the project
# ============================================================================

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    print_error "Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/projects/miniconda/en/latest/"
    exit 1
fi

print_header "2D Cylinder Flow Solver - Setup"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

print_success "Project root: $PROJECT_ROOT"

# Check if environment already exists
ENV_NAME="navier-cylinder"
if conda env list | grep -q "^$ENV_NAME "; then
    print_warning "Environment '$ENV_NAME' already exists. Removing it..."
    conda remove -n $ENV_NAME -y --all 2>/dev/null || true
fi

# Create conda environment
print_header "Creating Conda Environment"
echo "Creating environment: $ENV_NAME"

# Get Python version (use 3.10 for better MFEM compatibility)
PYTHON_VERSION="3.10"

conda create -n $ENV_NAME -y \
    python=$PYTHON_VERSION \
    cmake \
    make \
    gxx_linux-64 \
    gcc_linux-64 \
    gfortran_linux-64 \
    pkg-config \
    git

print_success "Conda environment created: $ENV_NAME"

# Activate the environment
echo "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

print_success "Environment activated"

# Install Python packages
print_header "Installing Python Packages"
pip install --upgrade pip
pip install numpy scipy matplotlib

print_success "Python packages installed"

# Check for MFEM installation
print_header "Checking MFEM Installation"

# Try to find MFEM
MFEM_FOUND=0
MFEM_DIR=""

# Check common locations
for potential_dir in \
    "$PROJECT_ROOT/../mfem-src" \
    "$HOME/mfem" \
    "/usr/local/mfem" \
    "$(find $HOME -maxdepth 3 -type d -name 'mfem-src' 2>/dev/null | head -1)"
do
    if [ -d "$potential_dir" ] && [ -f "$potential_dir/config.mk" ]; then
        MFEM_DIR="$potential_dir"
        MFEM_FOUND=1
        break
    fi
done

if [ $MFEM_FOUND -eq 1 ]; then
    print_success "MFEM found at: $MFEM_DIR"
else
    print_error "MFEM not found. You need to install MFEM first."
    echo ""
    echo "To install MFEM:"
    echo "  1. Download from: https://github.com/mfem/mfem"
    echo "  2. Configure and build:"
    echo "     cd mfem-src"
    echo "     make -j4"
    echo "  3. Place mfem-src in the parent directory or set MFEM_DIR below"
    echo ""
    print_warning "Attempting automatic MFEM setup..."

    # Offer to skip or provide path
    read -p "Enter MFEM installation directory (or press Enter to skip): " MFEM_PATH
    if [ -n "$MFEM_PATH" ] && [ -f "$MFEM_PATH/config.mk" ]; then
        MFEM_DIR="$MFEM_PATH"
        MFEM_FOUND=1
        print_success "MFEM directory set to: $MFEM_DIR"
    else
        print_error "MFEM not properly configured. Cannot proceed."
        exit 1
    fi
fi

# Build the project
print_header "Building Project"

# Create build directory
BUILD_DIR="$PROJECT_ROOT/build"
if [ -d "$BUILD_DIR" ]; then
    print_warning "Build directory exists. Cleaning..."
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

print_success "Build directory created: $BUILD_DIR"

# Configure with CMake
echo "Configuring with CMake..."
cmake -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_COMPILER=g++ \
    -DMFEM_DIR="$MFEM_DIR" \
    ..

print_success "CMake configuration complete"

# Build
echo "Building project (this may take a few minutes)..."
make -j$(nproc)

print_success "Build complete!"

# Verify build
if [ -f "$BUILD_DIR/navier_simple" ]; then
    print_success "Executable created: $BUILD_DIR/navier_simple"
else
    print_error "Build failed: executable not found"
    exit 1
fi

# Create activation script
print_header "Creating Environment Activation Script"

ACTIVATE_SCRIPT="$PROJECT_ROOT/activate.sh"
cat > "$ACTIVATE_SCRIPT" << 'ACTIVATE_EOF'
#!/bin/bash
# Activate the Navier-Stokes solver environment

ENV_NAME="navier-cylinder"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Activate the environment
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

if [ $? -eq 0 ]; then
    echo "✓ Environment '$ENV_NAME' activated"
    echo "Run: ./build/navier_simple -m cylinder_structured.mesh -Re 100 -dt 0.01 -t 0.5"
else
    echo "✗ Failed to activate environment"
    exit 1
fi
ACTIVATE_EOF

chmod +x "$ACTIVATE_SCRIPT"
print_success "Activation script created: $ACTIVATE_SCRIPT"

# Create quick start script
print_header "Creating Quick Start Script"

QUICKSTART_SCRIPT="$PROJECT_ROOT/quick_test.sh"
cat > "$QUICKSTART_SCRIPT" << 'QUICKSTART_EOF'
#!/bin/bash
# Quick test script for Navier-Stokes solver

# Activate environment
source ./activate.sh

# Check if mesh exists
if [ ! -f "cylinder_structured.mesh" ]; then
    echo "Generating mesh..."
    python3 generate_cylinder_mesh.py 100 100
fi

# Run simulation
echo "Running simulation..."
./build/navier_simple -m cylinder_structured.mesh -Re 100 -dt 0.01 -t 0.5

# Analyze results
if [ -f "forces_simple.dat" ]; then
    echo "Analyzing results..."
    python3 analyze_results.py
    echo "✓ Results saved to forces_simple.png"
fi
QUICKSTART_EOF

chmod +x "$QUICKSTART_SCRIPT"
print_success "Quick start script created: $QUICKSTART_SCRIPT"

# Print summary
print_header "Setup Complete!"
echo ""
echo "Project: 2D Incompressible Navier-Stokes Flow Past a Cylinder"
echo "Conda Environment: $ENV_NAME"
echo "Build Directory: $BUILD_DIR"
echo "Executable: $BUILD_DIR/navier_simple"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the environment:"
echo "   source activate.sh"
echo ""
echo "2. Generate a mesh (if not present):"
echo "   python3 generate_cylinder_mesh.py 100 100"
echo ""
echo "3. Run a simulation:"
echo "   ./build/navier_simple -m cylinder_structured.mesh -Re 100 -dt 0.01 -t 0.5"
echo ""
echo "4. Analyze results:"
echo "   python3 analyze_results.py"
echo ""
echo "Or run the quick test:"
echo "   ./quick_test.sh"
echo ""
print_success "Setup successful!"
