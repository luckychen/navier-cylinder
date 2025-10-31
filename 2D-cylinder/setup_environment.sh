#!/bin/bash

# ============================================================================
# Setup Script for 2D Cylinder Flow Navier-Stokes Solver
# This script sets up the conda environment, installs dependencies,
# downloads MFEM from source, compiles it, and builds the project
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

print_header "2D Cylinder Flow Solver - Complete Setup"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
PARENT_DIR="$(dirname "$PROJECT_ROOT")"

print_success "Project root: $PROJECT_ROOT"
print_success "Parent directory: $PARENT_DIR"

# ============================================================================
# Check for existing environment and packages
# ============================================================================
ENV_NAME="navier-cylinder"
ENV_EXISTS=0
PACKAGES_OK=0

# List of required packages
REQUIRED_CONDA_PACKAGES=(
    "python=3.10"
    "cmake"
    "make"
    "gxx_linux-64"
    "gcc_linux-64"
    "gfortran_linux-64"
    "pkg-config"
    "git"
    "bzip2"
    "zlib"
    "hypre"
    "metis"
    "openmpi"
    "lapack"
    "blas"
)

REQUIRED_PIP_PACKAGES=(
    "numpy"
    "scipy"
    "matplotlib"
    "scikit-learn"
)

# Check if environment exists
if conda env list | grep -q "^$ENV_NAME "; then
    ENV_EXISTS=1
    print_success "Environment '$ENV_NAME' already exists"
fi

# ============================================================================
# STEP 1: Create or Reuse Conda Environment
# ============================================================================
if [ $ENV_EXISTS -eq 1 ]; then
    print_header "Step 1: Checking Existing Conda Environment"

    # Activate the environment
    eval "$(conda shell.bash hook)"
    conda activate $ENV_NAME
    print_success "Environment activated: $ENV_NAME"

    # Check if all packages are installed
    echo "Verifying installed packages..."
    PACKAGES_OK=1

    for pkg in "${REQUIRED_CONDA_PACKAGES[@]}"; do
        # Extract package name (before = or @)
        pkg_name=$(echo "$pkg" | sed 's/=.*//' | sed 's/@.*//')
        if conda list -n $ENV_NAME | grep -q "^${pkg_name} "; then
            print_success "  ✓ $pkg_name installed"
        else
            print_warning "  ✗ $pkg_name NOT installed"
            PACKAGES_OK=0
        fi
    done

    if [ $PACKAGES_OK -eq 1 ]; then
        print_success "All conda packages already installed!"
    else
        print_warning "Some packages missing. Installing..."
        conda install -n $ENV_NAME -y "${REQUIRED_CONDA_PACKAGES[@]}"
        print_success "Packages installed"
    fi
else
    print_header "Step 1: Creating New Conda Environment"

    # Create conda environment with all required packages
    echo "Creating environment: $ENV_NAME with required packages"
    conda create -n $ENV_NAME -y \
        "${REQUIRED_CONDA_PACKAGES[@]}"

    print_success "Conda environment created: $ENV_NAME"

    # Activate the environment
    echo "Activating environment..."
    eval "$(conda shell.bash hook)"
    conda activate $ENV_NAME

    print_success "Environment activated"
fi

# Verify compilers are available
print_success "Checking compilers..."
which gcc > /dev/null && print_success "  GCC available" || print_error "  GCC NOT available"
which g++ > /dev/null && print_success "  G++ available" || print_error "  G++ NOT available"
which gfortran > /dev/null && print_success "  Gfortran available" || print_error "  Gfortran NOT available"
which cmake > /dev/null && print_success "  CMake available" || print_error "  CMake NOT available"

# ============================================================================
# STEP 2: Install/Verify Python Packages with pip
# ============================================================================
print_header "Step 2: Checking Python Packages"

echo "Verifying Python packages..."
PIP_PACKAGES_OK=1

for pkg in "${REQUIRED_PIP_PACKAGES[@]}"; do
    if pip show "$pkg" > /dev/null 2>&1; then
        print_success "  ✓ $pkg installed"
    else
        print_warning "  ✗ $pkg NOT installed"
        PIP_PACKAGES_OK=0
    fi
done

if [ $PIP_PACKAGES_OK -eq 1 ]; then
    print_success "All Python packages already installed!"
else
    print_warning "Some Python packages missing. Installing..."
    pip install --upgrade pip setuptools wheel
    pip install "${REQUIRED_PIP_PACKAGES[@]}"
    print_success "Python packages installed"
fi

# ============================================================================
# STEP 3: Check for MFEM and Download if Needed
# ============================================================================
print_header "Step 3: Checking/Installing MFEM"

MFEM_FOUND=0
MFEM_DIR=""
MFEM_BUILD_DIR=""

# Check if MFEM already exists
for potential_dir in \
    "$PARENT_DIR/mfem-src" \
    "$PROJECT_ROOT/../mfem-src" \
    "$HOME/mfem-src" \
    "$(find $HOME -maxdepth 2 -type d -name 'mfem-src' 2>/dev/null | head -1)"
do
    if [ -d "$potential_dir" ] && [ -f "$potential_dir/CMakeLists.txt" ]; then
        MFEM_DIR="$potential_dir"
        MFEM_FOUND=1
        print_success "Found existing MFEM at: $MFEM_DIR"
        break
    fi
done

# If MFEM not found, download and build it
if [ $MFEM_FOUND -eq 0 ]; then
    print_warning "MFEM not found locally. Downloading MFEM from GitHub..."

    # Set MFEM directory to parent
    MFEM_DIR="$PARENT_DIR/mfem-src"

    # Create parent directory if needed
    mkdir -p "$PARENT_DIR"

    # Clone MFEM
    cd "$PARENT_DIR"
    print_warning "Cloning MFEM repository (this may take a minute)..."
    git clone --depth 1 https://github.com/mfem/mfem.git mfem-src 2>&1 | tail -5

    print_success "MFEM cloned to: $MFEM_DIR"
fi

# Note: MFEM uses CMake build, library goes in: mfem-src/build/libmfem.a
# NOT in mfem-src/ root directory
MFEM_BUILD_DIR="$MFEM_DIR/build"
MFEM_LIB="$MFEM_BUILD_DIR/libmfem.a"

if [ -f "$MFEM_LIB" ]; then
    print_success "MFEM library found at: $MFEM_LIB ($(du -h $MFEM_LIB | cut -f1))"
    print_success "  → Location: $MFEM_DIR/build/"
    MFEM_FOUND=1
else
    print_warning "MFEM library not compiled. Building MFEM..."
    print_warning "  → Will create: $MFEM_DIR/build/"
    print_warning "  → Output file: libmfem.a"

    # Create build directory (IMPORTANT: CMake builds go in subdirectory, not root)
    mkdir -p "$MFEM_BUILD_DIR"
    cd "$MFEM_BUILD_DIR"

    print_header "Building MFEM (this may take 5-10 minutes)"

    # Configure MFEM with CMake
    echo "Configuring MFEM with CMake..."
    cmake "$MFEM_DIR" \
        -DCMAKE_BUILD_TYPE=Release \
        -DMFEM_USE_MPI=ON \
        -DMFEM_USE_METIS=ON \
        -DMFEM_USE_HYPRE=ON \
        -DCMAKE_CXX_COMPILER=g++ \
        -DCMAKE_C_COMPILER=gcc \
        -DCMAKE_Fortran_COMPILER=gfortran \
        2>&1 | tail -20

    print_success "MFEM configured"

    # Build MFEM
    echo "Compiling MFEM library..."
    make -j$(nproc) 2>&1 | tail -20

    if [ -f "$MFEM_LIB" ]; then
        print_success "MFEM compiled successfully: $MFEM_LIB ($(du -h $MFEM_LIB | cut -f1))"
    else
        print_error "MFEM build failed - libmfem.a not found"
        exit 1
    fi
fi

# ============================================================================
# STEP 4: Build the Navier-Stokes Project
# ============================================================================
print_header "Step 4: Building Navier-Stokes Project"

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
echo "Configuring project with CMake..."
cmake "$PROJECT_ROOT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_COMPILER=g++ \
    -DCMAKE_C_COMPILER=gcc \
    -DMFEM_DIR="$MFEM_DIR" \
    2>&1 | tail -20

print_success "CMake configuration complete"

# Build
echo "Building Navier-Stokes solver..."
make -j$(nproc) 2>&1 | tail -20

print_success "Build complete!"

# Verify build
if [ -f "$BUILD_DIR/navier_simple" ]; then
    print_success "Executable created: $BUILD_DIR/navier_simple ($(du -h $BUILD_DIR/navier_simple | cut -f1))"
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

# ============================================================================
# STEP 5: Create Activation and Quick-Start Scripts
# ============================================================================
print_header "Step 5: Creating Helper Scripts"

# Create activation script
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
    echo ""
    echo "Quick commands:"
    echo "  Generate mesh:     python3 generate_cylinder_mesh.py 100 100"
    echo "  Run simulation:    ./build/navier_simple -m cylinder_structured.mesh"
    echo "  Quick test:        bash quick_test.sh"
    echo "  Analyze results:   python3 analyze_results.py"
else
    echo "✗ Failed to activate environment"
    exit 1
fi
ACTIVATE_EOF

chmod +x "$ACTIVATE_SCRIPT"
print_success "Activation script created: $ACTIVATE_SCRIPT"

# Create quick start script
QUICKSTART_SCRIPT="$PROJECT_ROOT/quick_test.sh"
cat > "$QUICKSTART_SCRIPT" << 'QUICKSTART_EOF'
#!/bin/bash
# Quick test script for Navier-Stokes solver

# Activate environment
if [ ! -f "activate.sh" ]; then
    echo "Error: activate.sh not found. Please run from project root directory."
    exit 1
fi

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

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_header "Setup Complete!"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  2D Incompressible Navier-Stokes Flow Past a Cylinder         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Environment Setup:"
echo "  • Conda Environment:  $ENV_NAME"
echo "  • MFEM Source:        $MFEM_DIR"
echo "  • MFEM Build Output:  $MFEM_DIR/build/"
echo "  • MFEM Library:       $MFEM_LIB"
echo "  • Navier-Stokes Build: $BUILD_DIR"
echo "  • Executable:         $BUILD_DIR/navier_simple"
echo ""
echo "Next Steps:"
echo ""
echo "1. Activate the environment:"
echo "   source activate.sh"
echo ""
echo "2. Generate a mesh:"
echo "   python3 generate_cylinder_mesh.py 100 100"
echo ""
echo "3. Run a simulation:"
echo "   ./build/navier_simple -m cylinder_structured.mesh -Re 100 -dt 0.01 -t 0.5"
echo ""
echo "4. Analyze results:"
echo "   python3 analyze_results.py"
echo ""
echo "Or simply run the quick test:"
echo "   bash quick_test.sh"
echo ""
echo "For more information, see: README.md or START_HERE.md"
echo ""
print_success "All setup complete! You can now run your simulations."
