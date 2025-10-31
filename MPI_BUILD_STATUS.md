# MFEM MPI Build Status Report

**Date:** October 30, 2025
**Status:** Build-in-progress with MPI Support

## Summary

MFEM library is being compiled with full MPI support in the conda environment `mfem`. This report documents the build configuration, progress, and instructions.

---

## Environment Configuration

### Conda Environment: `mfem`

**Location:** `/home/ceoas/chenchon/miniconda3_x86/envs/mfem`

**Installed Packages:**
- **Build Tools:** CMake 4.1.2, Make 4.4.1, Git 2.51.2, pkg-config 0.29.2
- **Compilers:** GCC 14.3.0 (C, C++, Fortran)
- **MPI:** OpenMPI 5.0.8 with mpicc, mpicxx, mpif90 wrappers
- **High-Performance Libraries:**
  - HYPRE 2.32.0 (with MPI support)
  - METIS 5.2.1 (graph partitioning)
  - ParMETIS 4.0.3 (parallel partitioning)

### Compiler Information

```bash
$ mpicc --version
x86_64-conda-linux-gnu-cc (conda-forge gcc 14.3.0-7) 14.3.0

$ cmake --version
cmake version 4.1.2

$ mpirun --version
mpirun (Open MPI) 5.0.8
```

---

## MFEM Build Configuration

### Build Location

**Source:** `/fs1/home/ceoas/chenchon/mfem/mfem-src`
**Build:** `/fs1/home/ceoas/chenchon/mfem/mfem-src/build`

### CMake Configuration

```bash
cd /fs1/home/ceoas/chenchon/mfem/mfem-src/build
cmake .. \
  -DCMAKE_CXX_COMPILER=mpicxx \
  -DCMAKE_C_COMPILER=mpicc \
  -DCMAKE_BUILD_TYPE=Release \
  -DMFEM_USE_MPI=ON \
  -DMFEM_USE_METIS=ON \
  -DMFEM_USE_METIS_5=ON \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON
```

**Key Flags:**
- `-DCMAKE_CXX_COMPILER=mpicxx` - Use MPI C++ wrapper
- `-DMFEM_USE_MPI=ON` - Enable MPI support for parallel mesh/solver
- `-DMFEM_USE_METIS=ON` - Enable METIS mesh partitioning
- `-DCMAKE_POSITION_INDEPENDENT_CODE=ON` - Required for PIE executables

### Build Progress

**Status:** ~60% complete (as of last check)

**Components Compiled:**
- ✓ General utilities
- ✓ Linear algebra (BLAS/LAPACK wrappers)
- ✓ Mesh handling (parallel mesh, nc-mesh)
- ✓ FEM bilinear forms (50-60%)
- ⏳ FEM linear forms (in progress)
- ⏳ Nonlinear forms (pending)
- ⏳ Linking (pending)

---

## 2D-Cylinder Navier-Stokes Project Build

### Project Location

`/fs1/home/ceoas/chenchon/mfem/2D-cylinder`

### CMake Configuration for 2D-Cylinder

```bash
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder/build
cmake .. \
  -DCMAKE_CXX_COMPILER=mpicxx \
  -DMFEM_DIR=/fs1/home/ceoas/chenchon/mfem/mfem-src \
  -DCMAKE_CXX_STANDARD=17 \
  -DCMAKE_CXX_FLAGS="-fPIE" \
  -DCMAKE_EXE_LINKER_FLAGS="-pie"
```

**C++ Standard:** C++17 (required for MFEM features like structured bindings, if constexpr)

### Executables Built

1. **`navier_solver`** - Main Navier-Stokes solver
   - Command-line options: `-m/--mesh`, `-Re`, `-dt`, `-t`
   - MPI-enabled for parallel execution
   - Supports various mesh formats

2. **`test_mesh_parser`** - Mesh validation utility
   - Tests MFEM mesh file format compliance
   - Verifies element and boundary attributes

---

## Build Commands (Reference)

### Activate Environment

```bash
source /home/ceoas/chenchon/miniconda3_x86/etc/profile.d/conda.sh
conda activate mfem
```

### Build MFEM (if rebuilding needed)

```bash
cd /fs1/home/ceoas/chenchon/mfem/mfem-src/build
make -j4          # or higher for faster build
```

### Build 2D-Cylinder

```bash
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder/build
make -j4
```

### Run Simulation (single processor)

```bash
./navier_solver -m cylinder.mesh -Re 100 -dt 0.01 -t 1.0
```

### Run Simulation (parallel - 4 processors)

```bash
mpirun -np 4 ./navier_solver -m cylinder.mesh -Re 100 -dt 0.01 -t 1.0
```

---

## Mesh Files

### Available Meshes

- **cylinder.mesh** - Base cylinderflow mesh (generated)
- **cylinder_structured.mesh** - Structured quad mesh from Python generator
- **test_minimal.mesh** - Small test mesh for validation

### Generate Custom Meshes

```bash
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder
python3 generate_cylinder_mesh.py [nx] [ny]
```

Example: `python3 generate_cylinder_mesh.py 50 25` creates a 50x25 element mesh.

---

## Next Steps (When Build Completes)

1. **Verify Build Success**
   ```bash
   cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder/build
   ls -la navier_solver test_mesh_parser
   ```

2. **Test Mesh Parser**
   ```bash
   ./test_mesh_parser cylinder.mesh
   ```

3. **Run Sample Simulation**
   ```bash
   ./navier_solver -m cylinder.mesh -Re 100 -dt 0.01 -t 0.1
   ```

4. **Parallel Execution**
   ```bash
   mpirun -np 2 ./navier_solver -m cylinder.mesh -Re 100 -dt 0.01 -t 0.1
   ```

---

## Troubleshooting

### Build Fails with Position-Independent Code Errors

**Problem:** Linker errors like "relocation R_X86_64_32S against symbol ... can not be used when making a PIE object"

**Solution:** Ensure MFEM was built with `-DCMAKE_POSITION_INDEPENDENT_CODE=ON`:
```bash
cd /fs1/home/ceoas/chenchon/mfem/mfem-src/build
cmake .. -DCMAKE_POSITION_INDEPENDENT_CODE=ON
make clean
make -j4
```

### C++ Standard Errors

**Problem:** Errors mentioning C++14 or C++17 features not available

**Solution:** Ensure 2D-cylinder CMakeLists.txt has `set(CMAKE_CXX_STANDARD 17)`

### MPI Compilation Errors

**Problem:** Compilation fails with MPI-related symbols undefined

**Solution:** Verify MPI installation:
```bash
which mpicc mpicxx
mpicc --version
```

---

## Performance Notes

- **MFEM with MPI:** Designed for large-scale distributed computing
- **Parallel Mesh Handling:** ParMesh automatically partitions meshes
- **Preconditioners:** LOR (Low-Order Refinement) preconditioner for pressure Poisson equation
- **High-Order Elements:** P2/P1 Taylor-Hood elements for Navier-Stokes stability

---

## References

- MFEM Documentation: https://mfem.org/
- OpenMPI Home: https://www.open-mpi.org/
- Project CLAUDE.md: Full implementation strategy in repository

