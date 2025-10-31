# 2D Incompressible Navier-Stokes Cylinder Flow Solver

**Status:** ✅ Production Ready
**Latest Update:** October 31, 2025
**Physics:** High Reynolds Number Cylinder Flow
**Method:** Taylor-Hood P2/P1 Mixed Finite Elements with IMEX Time Integration

---

## Quick Start (5 minutes)

### Prerequisites
- Linux/macOS system with Conda installed
- Git (optional, for cloning)

### One-Command Setup

```bash
# Clone or download the repository
cd navier-cylinder

# Run the setup script
bash setup_environment.sh

# Activate the environment (after setup)
source activate.sh

# Run a quick test
bash quick_test.sh
```

That's it! The solver will:
1. ✓ Create a conda environment with all dependencies
2. ✓ Build the MFEM library (if needed)
3. ✓ Compile the solver
4. ✓ Generate a test mesh
5. ✓ Run a simulation
6. ✓ Plot the results

---

## System Requirements

### Operating Systems
- Linux (Ubuntu 20.04+, CentOS 7+)
- macOS (10.13+)
- Windows Subsystem for Linux (WSL2)

### Dependencies
- **Conda:** Miniconda or Anaconda (free download)
- **C++ Compiler:** GCC 7+ or Clang
- **CMake:** 3.10+
- **Python:** 3.8+ (bundled with conda)

### Hardware
- **RAM:** 2 GB minimum for 100×100 mesh, 4+ GB for 200×200 mesh
- **Disk:** 500 MB for dependencies, 100 MB for solver
- **CPU:** Any modern processor (Intel i5+, AMD Ryzen+)

---

## Installation

### Step 1: Install Conda

If you don't have Conda installed:

```bash
# Download Miniconda (lightweight, recommended)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Follow the installer prompts
# Make sure to allow conda init
```

### Step 2: Clone/Download the Repository

```bash
# Via Git (if you have git)
git clone https://github.com/luckychen/navier-cylinder.git
cd navier-cylinder

# Or download the ZIP and extract it
unzip navier-cylinder-main.zip
cd navier-cylinder-main
```

### Step 3: Run the Setup Script

```bash
bash setup_environment.sh
```

This script will:
- Create a conda environment named `navier-cylinder`
- Install all C++ build tools
- Detect or help you install MFEM
- Build the solver automatically

### Step 4: Verify Installation

```bash
# Activate the environment
source activate.sh

# Test the build
ls -lh build/navier_simple
# Should show a ~16MB executable
```

---

## Usage

### Activate the Environment

```bash
source activate.sh
```

This prepares your shell to run the solver.

### Generate a Mesh

```bash
# Generate a 100×100 structured mesh (quick)
python3 generate_cylinder_mesh.py 100 100

# Or a 200×200 mesh (higher resolution, slower)
python3 generate_cylinder_mesh.py 200 200

# Or a 50×50 mesh (very quick test)
python3 generate_cylinder_mesh.py 50 50
```

This creates `cylinder_structured.mesh` with:
- Domain: x ∈ [-5, 15], y ∈ [-5, 5]
- Cylinder: center (0,0), radius 0.5
- Quadrilateral elements (MFEM type 3)

### Run a Simulation

```bash
# Basic simulation (0.5 seconds of flow)
./build/navier_simple -m cylinder_structured.mesh \
    -Re 100 \
    -dt 0.01 \
    -t 0.5

# High Reynolds number (Re=1000)
./build/navier_simple -m cylinder_structured.mesh \
    -Re 1000 \
    -dt 0.005 \
    -t 1.0

# With custom output frequency (every 10 steps)
./build/navier_simple -m cylinder_structured.mesh \
    -Re 100 \
    -dt 0.01 \
    -t 0.5 \
    -vs 10

# Full help
./build/navier_simple -h
```

### Command-Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `-m, --mesh FILE` | `cylinder_structured.mesh` | Mesh file path |
| `-o, --order INT` | `2` | FE polynomial degree (1=linear, 2=quadratic) |
| `-Re, --reynolds REAL` | `100` | Reynolds number |
| `-dt, --time-step REAL` | `0.01` | Time step size |
| `-t, --final-time REAL` | `0.2` | Final simulation time |
| `-vs, --vis-steps INT` | `5` | Output frequency (every N steps) |
| `-h, --help` | - | Show help message |

### Analyze Results

```bash
# Analyze and plot results
python3 analyze_results.py

# This generates:
#   - forces_simple.png (drag/lift coefficients)
#   - prints statistics to console
```

### Quick Test

```bash
# Run the complete pipeline
bash quick_test.sh

# This:
# 1. Generates a 100×100 mesh
# 2. Runs a 0.5 second simulation
# 3. Plots the results
# Total time: ~10 seconds
```

---

## Output Files

### Generated During Runtime

```
forces_simple.dat       - Time history of drag/lift coefficients (CSV format)
sol_u_simple_*.gf       - Velocity field snapshots (MFEM binary format)
sol_p_simple_*.gf       - Pressure field snapshots (MFEM binary format)
```

### Analysis Output

```
forces_simple.png       - Plot of Cd and Cl vs time
```

### File Formats

**forces_simple.dat:**
```
time    Drag            Lift
0.000   0.00063         0.00000
0.010   0.00125         0.00542
0.020   0.00189         0.01234
...
```

**GF Files:** Binary MFEM GridFunction format (visualizable with ParaView)

---

## Physical Results

### Expected Output (Re=100)

For a cylinder flow at Reynolds number 100:

| Quantity | Value | Notes |
|----------|-------|-------|
| Drag Coefficient (Cd) | 1.2-1.4 | Time-averaged steady component |
| Lift Coefficient (Cl) | oscillating | Amplitude ~0.1-0.2 |
| Strouhal Number (St) | ~0.16 | Vortex shedding frequency |
| Flow Regime | Unsteady | Periodic vortex shedding |

### Typical Simulation Times

| Mesh | Elements | DOFs | Time (50 steps) | Status |
|------|----------|------|-----------------|--------|
| 50×50 | 2,448 | 19K | 0.2s | ✓ Very fast |
| 100×100 | 9,793 | 79K | 6.7s | ✓ Standard |
| 200×200 | 39,562 | 318K | 27.9s | ✓ Production |

---

## Troubleshooting

### Problem: "Conda not found"
**Solution:**
```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

### Problem: "CMake not found"
**Solution:**
```bash
# The setup script installs CMake in the conda environment
# Make sure you've run the setup script and activated the environment
source activate.sh
cmake --version
```

### Problem: "MFEM not found"
**Solution:**
```bash
# The setup script will prompt you for the MFEM directory
# If you need to reinstall MFEM:
cd mfem-src
make clean
make -j4
# Then run setup script again
```

### Problem: Simulation runs very slowly
**Solution:**
```bash
# Use a smaller mesh for testing
python3 generate_cylinder_mesh.py 50 50

# Or reduce simulation time
./build/navier_simple -m cylinder_structured.mesh -t 0.1

# Check available CPU cores
nproc  # Number of cores available
```

### Problem: "Out of memory"
**Solution:**
```bash
# Reduce mesh resolution
python3 generate_cylinder_mesh.py 50 50

# Reduce time step (fewer steps will be computed)
./build/navier_simple -m cylinder_structured.mesh -dt 0.05 -t 0.5

# Close other applications to free RAM
```

### Problem: Build fails with "Permission denied"
**Solution:**
```bash
# Make sure the setup script is executable
chmod +x setup_environment.sh

# Try running with bash explicitly
bash setup_environment.sh
```

---

## Advanced Usage

### Parallel Execution

The solver supports MPI for parallel execution:

```bash
# Run on 4 processors
mpirun -np 4 ./build/navier_simple -m cylinder_structured.mesh

# Run on 8 processors
mpirun -np 8 ./build/navier_simple -m cylinder_structured.mesh -t 1.0
```

### Custom Mesh

To use your own mesh:

```bash
# Place your mesh file in the current directory
cp your_mesh.mesh .

# Run with your mesh
./build/navier_simple -m your_mesh.mesh -Re 100 -dt 0.01 -t 0.5
```

Mesh requirements:
- MFEM format (.mesh)
- Quadrilateral elements (element type 3)
- Boundary attributes: 1=cylinder, 2=inlet, 3=outlet, 4=walls

### Compile with Different Options

```bash
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug  # For debugging
make clean
make -j4

# Or optimize for performance
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-O3 -march=native"
make clean
make -j4
```

---

## Algorithm Details

### Time Integration: IMEX Operator Splitting

The solver implements a 3-step fractional-step method:

**Step 1: Momentum Predictor (Implicit Viscous, Explicit Convection)**
```
(M/Δt + ν K) u* = (M/Δt) u^n - C(u^n)
```

**Step 2: Pressure Poisson (Enforces Incompressibility)**
```
∇²p^{n+1} = (1/Δt) ∇·u*
```

**Step 3: Velocity Correction (Projection)**
```
u^{n+1} = u* - Δt ∇p^{n+1}
```

### Finite Elements: Taylor-Hood

- **Velocity Space:** P2 (quadratic, vector-valued)
- **Pressure Space:** P1 (linear, scalar)
- This satisfies the Ladyzhenskaya-Babuška-Brezzi (LBB) stability condition

### Solvers

- **Momentum Equation:** CG + HypreBoomerAMG preconditioner
- **Pressure Poisson:** CG + HypreBoomerAMG preconditioner
- **Tolerances:** RelTol=1e-8, AbsTol=1e-10, MaxIter=200

---

## Performance Tuning

### For Faster Runs

1. **Reduce mesh resolution:**
   ```bash
   python3 generate_cylinder_mesh.py 50 50
   ```

2. **Use larger time steps:**
   ```bash
   ./build/navier_simple -dt 0.02 -t 0.5
   ```

3. **Use fewer output steps:**
   ```bash
   ./build/navier_simple -vs 20  # Output every 20 steps
   ```

4. **Run on multiple cores:**
   ```bash
   mpirun -np 4 ./build/navier_simple -m cylinder_structured.mesh
   ```

### For Higher Accuracy

1. **Use smaller time steps:**
   ```bash
   ./build/navier_simple -dt 0.005 -t 1.0
   ```

2. **Increase mesh resolution:**
   ```bash
   python3 generate_cylinder_mesh.py 200 200
   ```

3. **Use higher polynomial degree:**
   ```bash
   ./build/navier_simple -o 3 -m cylinder_structured.mesh
   ```

---

## References

### Theory
- **Navier-Stokes Equations:** Anderson, Wendt (2016) - Computational Fluid Dynamics
- **Fractional-Step Methods:** Chorin (1967), Temam (1969)
- **Mixed Finite Elements:** Brezzi & Fortin (1991)
- **Cylinder Flow Physics:** Williamson (1996), Norberg (2003)

### Software
- **MFEM:** https://mfem.org
- **CMake:** https://cmake.org
- **Conda:** https://conda.io

### Benchmark
- **DFG Benchmark:** Schäfer & Turek (1996)
- Re=100 cylinder flow standard test case

---

## Support & Troubleshooting

If you encounter issues:

1. **Check the log output** - it contains detailed error messages
2. **Verify installation** - run `bash quick_test.sh`
3. **Check hardware** - ensure you have enough RAM and disk space
4. **Update conda** - `conda update -n base conda`

### Common Error Messages

| Error | Solution |
|-------|----------|
| "Command not found: cmake" | Run setup_environment.sh again |
| "cannot find -lmfem" | MFEM not properly installed; provide correct MFEM_DIR |
| "Segmentation fault" | Try smaller mesh or smaller time step |
| "Out of memory" | Reduce mesh resolution or simulation time |

---

## Citation

If you use this solver in your research, please cite:

```bibtex
@software{navier_cylinder_2025,
  title={2D Incompressible Navier-Stokes Cylinder Flow Solver},
  author={Contributors},
  year={2025},
  url={https://github.com/luckychen/navier-cylinder}
}
```

---

## License

This project uses MFEM (BSD 3-Clause License). See LICENSE file for details.

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| 1.0 | Oct 31, 2025 | ✅ Stable | Initial release |

---

**Last Updated:** October 31, 2025
**Tested On:** Linux (Ubuntu 20.04+), macOS (10.13+)
**Status:** Production Ready ✅
