# Build and Run Guide - 2D Cylinder Flow Simulation

## Quick Start

### Prerequisites Checked
- ✓ C++ compiler (GCC 11.4.1)
- ✓ CMake 3.26.5
- ✓ Python 3 (for mesh generation)
- ✓ Git
- ✓ Standard Unix tools (make, bash, etc.)

## Step-by-Step Build Instructions

### 1. Navigate to Project Directory

```bash
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder
```

### 2. Create Build Directory

```bash
mkdir -p build
cd build
```

### 3. Configure with CMake

```bash
cmake -DCMAKE_BUILD_TYPE=Release -DMFEM_DIR=../mfem-src ..
```

**Expected output:**
```
-- MFEM_DIR: ../mfem-src
-- Build type: Release
-- Configuring done (X.Xs)
-- Generating done
-- Build files have been written to: ...
```

### 4. Build the Project

```bash
make -j4
```

This will:
1. Generate the cylinder mesh (via Python script)
2. Compile the Navier-Stokes solver
3. Link against MFEM library

**Build time:** ~30-60 seconds depending on system

**Expected output:**
```
[ 50%] Generating mesh
Mesh generated: cylinder.mesh
[100%] Building CXX object CMakeFiles/navier_solver.dir/navier_solver.cpp.o
[100%] Linking CXX executable navier_solver
[100%] Built target navier_solver
```

### 5. Verify Build Success

```bash
ls -la navier_solver
```

You should see the executable with size ~2-5 MB.

## Running the Simulation

### Basic Execution (Single Processor)

```bash
./navier_solver
```

**Default parameters:**
- Reynolds number: 1000
- Time step: 0.001
- Final time: 100 time units
- Mesh refinement: 0

**Expected output:**
```
Navier-Stokes Solver Configuration:
  Reynolds Number: 1000
  Kinematic Viscosity: 0.001
  Time Step: 0.001
  Final Time: 100
  Number of Steps: 100000

Mesh loaded: 3200 elements
              3381 vertices
              640 boundary elements

FE Spaces created:
  Velocity DOFs: 50682
  Pressure DOFs: 5472

Boundary conditions applied
Bilinear forms assembled
Solvers initialized

=== Starting Time Integration ===
Step 0 / 100000 (t = 0)
Step 10 / 100000 (t = 0.01)
...
```

### Run with Custom Parameters

```bash
# Lower Reynolds number for faster testing
./navier_solver -Re 500 -dt 0.002 -t 50

# Higher Reynolds number (longer computation)
./navier_solver -Re 2000 -dt 0.0005 -t 200

# Refined mesh
./navier_solver -r 1 -Re 1000 -dt 0.001 -t 100
```

**Command-line options:**
```
-r, --refine VALUE          : Number of mesh refinement levels (default: 0)
-Re, --reynolds VALUE       : Reynolds number (default: 1000)
-dt, --time-step VALUE      : Time step size (default: 0.001)
-t, --final-time VALUE      : Final simulation time (default: 100)
-h, --help                  : Print help message
```

### Typical Simulation Runtimes

| Reynolds | Time-Step | Final Time | DOF       | Est. Runtime |
|----------|-----------|------------|-----------|--------------|
| 500      | 0.002     | 50         | ~50k      | 5-10 min     |
| 1000     | 0.001     | 100        | ~50k      | 30-60 min    |
| 1000     | 0.001     | 200        | ~50k      | 60-120 min   |
| 2000     | 0.0005    | 100        | ~50k      | 60-90 min    |

## Output Files

After running, the simulation generates:

### 1. Forces File (`forces.dat`)
CSV format with columns: Time, Drag, Lift

```
Time,Drag,Lift
0.000000,0.000000,0.000000
0.010000,1.203456,-0.021345
0.020000,1.204123,-0.043567
...
```

### 2. Solution Files
- `sol_u_0000.gf` - Velocity at t=0
- `sol_u_0001.gf` - Velocity at t=10
- `sol_u_0002.gf` - Velocity at t=20
- `sol_p_0000.gf` - Pressure at t=0
- `sol_p_0001.gf` - Pressure at t=10
- etc.

These are in MFEM's binary GridFunction format.

## Post-Processing and Visualization

### 1. Quick Analysis of Forces

```bash
python3 ../plot_forces.py forces.dat
```

This generates:
- `forces_history.png` - Drag/lift time series and phase portrait
- `spectrum.png` - Frequency spectrum (for Strouhal number calculation)

**Required Python packages:**
```bash
pip install matplotlib scipy numpy
```

### 2. Understanding the Output

**forces_history.png** contains 4 subplots:
1. **Top-left**: Drag coefficient vs time
2. **Top-right**: Lift coefficient vs time
3. **Bottom-left**: Phase portrait (drag vs lift)
4. **Bottom-right**: Total force magnitude vs time

**Key observations:**
- After initial transient (~10-20 time units), drag/lift oscillate periodically
- Lift has nearly zero mean (by symmetry)
- Drag oscillates around average value ~1.2-1.3 for Re=1000

**spectrum.png** shows:
- Power spectral density (PSD) of lift oscillations
- Sharp peak at vortex shedding frequency
- Frequency · Diameter / U_∞ = **Strouhal number**

### 3. Converting to ParaView Format

To visualize velocity/pressure fields in ParaView:

```python
#!/usr/bin/env python3
import struct
import numpy as np

def gf_to_vtk(gf_file, mesh_file, output_file):
    """Convert MFEM GridFunction to VTK format"""
    # Load mesh vertices and connectivity
    vertices, cells = load_mfem_mesh(mesh_file)

    # Load solution data
    data = load_mfem_gf(gf_file)

    # Write VTK format
    write_vtk(vertices, cells, data, output_file)

# See VISUALIZATION_GUIDE.md for full implementation
```

See **VISUALIZATION_GUIDE.md** for complete visualization instructions.

## Troubleshooting

### Build Errors

**Error: "mfem.hpp: No such file or directory"**
```bash
# Solution: Ensure MFEM_DIR points to source directory
cmake -DMFEM_DIR=../mfem-src ..
make clean
make -j4
```

**Error: "libmfem.a not found"**
```bash
# Solution: Build MFEM first
cd ../mfem-src/build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
cd ../../2D-cylinder/build
cmake ..
make -j4
```

**Error: Unresolved symbol errors during linking**
```bash
# May be MFEM hypre/lapack dependencies
# Rebuild MFEM with all dependencies
cd ../mfem-src/build
cmake -DMFEM_USE_HYPRE=ON -DMFEM_USE_LAPACK=ON ..
make -j4
```

### Runtime Errors

**Error: "Mesh file 'cylinder.mesh' not found"**
```bash
# Solution: Regenerate mesh
cd ..
python3 generate_mesh.py
cd build
./navier_solver
```

**Error: Solver divergence / NaN values**
```bash
# Solution: Reduce time step
./navier_solver -dt 0.0005  # Half the default

# Or reduce Reynolds number
./navier_solver -Re 500

# Or use finer mesh
./navier_solver -r 1
```

**Error: Program hangs or runs very slowly**
```bash
# Check CPU usage
top

# If solver is iterating too much, reduce tolerance or check mesh quality
# View solver iterations by adding debug output to source code
```

### Memory Issues

**Error: Segmentation fault or "out of memory"**
```bash
# Current problem size: ~50k velocity DOF = ~2.5 GB peak
# Solutions:
# 1. Reduce mesh size (change nx, ny in generate_mesh.py)
# 2. Use fewer time steps (-t 10 instead of -t 100)
# 3. Run on HPC node with more memory
```

## Performance Optimization

### Compiler Flags

The CMakeLists.txt uses:
- `-O3` optimization level
- `-march=native` for CPU-specific optimizations

For additional performance:

```bash
# Very aggressive optimization (may take longer to compile)
cmake -DCMAKE_CXX_FLAGS="-O3 -march=native -flto" ..
make -j4
```

### Multi-threaded Execution

OpenMP support (if available):
```bash
export OMP_NUM_THREADS=4
./navier_solver
```

### MPI Parallelization (Future)

Once MPI support is implemented:
```bash
mpirun -np 4 ./navier_solver
```

## Monitoring Simulation Progress

### Real-time Monitoring

```bash
# In another terminal, monitor output file size
watch -n 5 "ls -lh forces.dat"

# Or count lines (time steps)
watch -n 10 "wc -l forces.dat"
```

### Logging to File

```bash
./navier_solver -Re 1000 > simulation.log 2>&1 &
tail -f simulation.log
```

## Stopping and Resuming

The current implementation does **not** support checkpointing/restart.

To stop a long-running simulation:
```bash
# Press Ctrl+C to interrupt

# To resume: modify final time in code or create checkpoint feature
```

## File Management

### Archiving Results

```bash
# Compress all output files
tar -czf cylinder_results_re1000.tar.gz forces.dat sol_u_*.gf sol_p_*.gf

# Transfer to local machine
scp -r results/ local-machine:~/simulations/
```

### Cleanup

```bash
# Remove all output files
rm -f sol_*.gf forces.dat

# Clean build artifacts
make clean

# Remove everything and rebuild
rm -rf build/
mkdir build && cd build && cmake .. && make -j4
```

## Next Steps

1. **Run the simulation** with default parameters
2. **Analyze forces** using `plot_forces.py`
3. **Study results** against literature values for cylinder flow
4. **Modify code** to implement new features (turbulence models, higher Re, etc.)
5. **Parallelize** using MPI for larger problems

## References

- MFEM Build System: https://mfem.org/building/
- CMake Documentation: https://cmake.org/cmake/help/latest/
- Cylinder Flow References:
  - Williamson, C.H.K. (1996) "Vortex dynamics in the cylinder wake"
  - Norberg, C. (2003) "Fluid mechanics of cylinder flow" (comprehensive review)

---

For detailed visualization instructions, see **VISUALIZATION_GUIDE.md**

For simulation theory and parameters, see **README.md**

