#!/bin/bash

# ============================================================================
# Quick Test Script for 2D Cylinder Flow Navier-Stokes Solver
# ============================================================================

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Verify environment is set up
if [ ! -f "build/navier_simple" ]; then
    echo "Error: Executable not found. Run setup_environment.sh first."
    exit 1
fi

print_header "2D Cylinder Flow - Quick Test"

# Activate environment if needed
if ! command -v python3 &> /dev/null; then
    if [ -f "activate.sh" ]; then
        source activate.sh
    fi
fi

# Step 1: Generate mesh
print_header "Step 1: Generating Mesh"
if [ ! -f "cylinder_structured.mesh" ]; then
    echo "Mesh not found. Generating 100x100 mesh..."
    python3 generate_cylinder_mesh.py 100 100
    print_success "Mesh generated: cylinder_structured.mesh"
else
    print_success "Using existing mesh: cylinder_structured.mesh"
fi

# Step 2: Run simulation
print_header "Step 2: Running Simulation"
echo "Simulating 0.5 seconds of flow at Re=100..."
echo "This may take 10-20 seconds on a typical laptop..."
echo ""

./build/navier_simple -m cylinder_structured.mesh \
    -Re 100 \
    -dt 0.01 \
    -t 0.5 \
    -vs 5

print_success "Simulation complete!"

# Step 3: Analyze results
print_header "Step 3: Analyzing Results"

if [ -f "forces_simple.dat" ]; then
    echo "Generating plots..."
    python3 analyze_results.py

    if [ -f "forces_simple.png" ]; then
        print_success "Results saved to forces_simple.png"
        print_success "Force data saved to forces_simple.dat"
    fi
else
    echo "Warning: No force data found"
fi

# Summary
print_header "Test Complete!"
echo ""
echo "Summary:"
echo "  ✓ Mesh: cylinder_structured.mesh (100x100 elements)"
echo "  ✓ Simulation: 0.5 seconds at Re=100"
echo "  ✓ Output: forces_simple.png and forces_simple.dat"
echo ""
echo "Next steps:"
echo "  - View results: forces_simple.png"
echo "  - Run with different parameters:"
echo "    ./build/navier_simple -m cylinder_structured.mesh -Re 200 -t 1.0"
echo "  - Generate higher resolution mesh:"
echo "    python3 generate_cylinder_mesh.py 200 200"
echo ""
print_success "All done!"
