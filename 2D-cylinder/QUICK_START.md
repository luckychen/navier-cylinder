# Quick Start Guide - 2D Cylinder Flow Simulation

## TL;DR - Get Started in 30 seconds

```bash
# Navigate to project
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder

# When MFEM build completes, build the solver (2-5 min)
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DMFEM_DIR=../mfem-src ..
make -j4

# Run a quick test (5-10 min)
./navier_solver -Re 1000 -dt 0.001 -t 5

# Analyze results
python3 ../plot_forces.py forces.dat
```

---

## Status Check

### Is MFEM Ready?

```bash
ls -lh /fs1/home/ceoas/chenchon/mfem/mfem-src/build/libmfem.a
# If file exists (~800MB), MFEM is ready!
```

Monitor progress:
```bash
# Terminal 1: Monitor the watchshell
tail -f /dev/shm/mfem_build.log 2>/dev/null || echo "Not found"

# Or check ranlib process
ps aux | grep ranlib

# Or watch file size growth
watch -n 5 'ls -lh /fs1/home/ceoas/chenchon/mfem/mfem-src/build/libmfem.a 2>/dev/null || echo Building...'
```

---

## Full Workflow

### Phase 1: Wait for MFEM (5-20 minutes)
- MFEM library is currently building
- Status: In ranlib (final archiving) phase
- No action needed, it will complete automatically

### Phase 2: Build Solver (2-5 minutes)
Once MFEM is ready:

```bash
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DMFEM_DIR=../mfem-src ..
make -j4
```

Verify build succeeded:
```bash
ls -la navier_solver    # Should be ~2-5 MB executable
file navier_solver      # Should show "ELF 64-bit executable"
./navier_solver --help  # Should print help message
```

### Phase 3: Run Simulation (5-120 minutes, depends on parameters)

**Quick Test** (5-10 minutes):
```bash
./navier_solver -Re 1000 -dt 0.001 -t 5
```

**Standard Run** (30-60 minutes):
```bash
./navier_solver -Re 1000 -dt 0.001 -t 100
```

**Extended Run** (2-3 hours):
```bash
./navier_solver -Re 1000 -dt 0.001 -t 200
```

### Phase 4: Analyze Results (5-10 minutes)

```bash
# Generate analysis plots
python3 ../plot_forces.py forces.dat

# View results
ls -lh forces_history.png spectrum.png
cat forces.dat | head -20  # First 20 time steps
```

### Phase 5: Download and Visualize Locally

From your local workstation:

```bash
# Create local directory
mkdir ~/cylinder_flow && cd ~/cylinder_flow

# Download results
scp chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/build/{forces.dat,*.png} ./
scp chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/build/sol_*.gf ./

# View images
open *.png        # macOS
eog *.png         # Linux
```

---

## Parameter Quick Reference

### Time Step & Reynolds
```bash
# Fast testing (Re=500, quick)
./navier_solver -Re 500 -dt 0.002 -t 10

# Standard (Re=1000)
./navier_solver -Re 1000 -dt 0.001 -t 100

# High Reynolds (Re=2000, smaller dt)
./navier_solver -Re 2000 -dt 0.0005 -t 100

# Very fine mesh
./navier_solver -r 2 -Re 1000 -dt 0.001 -t 50
```

---

## Expected Results

After a typical 100-time-unit simulation at Re=1000:

1. **forces.dat** - CSV with drag/lift history
   - ~100,000 lines (one per time step)
   - Columns: Time, Drag, Lift

2. **sol_u_*.gf** - 10 velocity solution snapshots
   - Files: sol_u_0000.gf through sol_u_0009.gf
   - Each ~30-50 MB

3. **sol_p_*.gf** - 10 pressure solution snapshots
   - Files: sol_p_0000.gf through sol_p_0009.gf
   - Each ~3-5 MB

4. **forces_history.png** - 4-subplot figure showing:
   - Drag vs time
   - Lift vs time
   - Phase portrait (drag vs lift)
   - Total force magnitude

5. **spectrum.png** - Frequency spectrum showing vortex shedding frequency

### Key Numbers (Re=1000)
- Drag coefficient: C_D ≈ 1.2-1.3 (mean)
- Strouhal number: St ≈ 0.215
- Oscillation period: ~4.6-4.8 time units

---

## File Organization

```
/fs1/home/ceoas/chenchon/mfem/
├── README.md
├── CLAUDE.md                    # Original requirements
├── PROJECT_SETUP_SUMMARY.md     # Full project overview
├── mfem-src/                    # MFEM library source
│   └── build/
│       └── libmfem.a            # [Being built]
└── 2D-cylinder/                 # Main project folder
    ├── CMakeLists.txt
    ├── navier_solver.cpp        # Main solver
    ├── generate_mesh.py         # Mesh generator
    ├── plot_forces.py           # Analysis tool
    ├── cylinder.mesh            # Mesh file
    ├── README.md                # Full documentation
    ├── BUILD_AND_RUN_GUIDE.md   # Build instructions
    ├── VISUALIZATION_GUIDE.md   # Visualization help
    ├── QUICK_START.md           # This file
    └── build/                   # [To be created]
        ├── navier_solver        # Executable [to build]
        ├── forces.dat           # [Generated at runtime]
        ├── sol_u_*.gf           # [Generated at runtime]
        ├── sol_p_*.gf           # [Generated at runtime]
        └── *.png                # [Generated at runtime]
```

---

## Troubleshooting

### Problem: "MFEM build still in progress"
**Solution**: Wait 5-20 more minutes, it's in the ranlib phase
```bash
watch -n 10 'ps aux | grep ranlib'  # See if still running
```

### Problem: CMake can't find MFEM
**Solution**: Check MFEM build completed
```bash
ls /fs1/home/ceoas/chenchon/mfem/mfem-src/build/libmfem.a
cmake -DMFEM_DIR=/fs1/home/ceoas/chenchon/mfem/mfem-src ..
```

### Problem: Solver diverges / NaN in output
**Solution**: Reduce time step or Reynolds number
```bash
./navier_solver -Re 500 -dt 0.002 -t 10  # Simpler case
```

### Problem: "Out of memory" error
**Solution**: Reduce simulation parameters
```bash
./navier_solver -Re 1000 -dt 0.001 -t 10  # Shorter run
```

---

## What Each File Does

| File | Purpose |
|------|---------|
| **navier_solver.cpp** | Main solver code - Navier-Stokes implementation |
| **generate_mesh.py** | Creates cylinder.mesh from scratch |
| **cylinder.mesh** | Computational mesh (quadrilaterals, ~3200 elements) |
| **plot_forces.py** | Analyzes forces.dat and generates plots |
| **CMakeLists.txt** | Build configuration |
| **forces.dat** | Output - drag and lift time history |
| **sol_u_*.gf** | Output - velocity snapshots |
| **sol_p_*.gf** | Output - pressure snapshots |

---

## Next Steps After First Run

1. **Analyze the results**: `python3 plot_forces.py forces.dat`
2. **Read the full documentation**: `README.md`
3. **Study the visualizations**: `forces_history.png` and `spectrum.png`
4. **Download locally**: Use scp to get results to your workstation
5. **Try different parameters**: Re-run with different Re, dt, or simulation time
6. **Modify solver**: Edit navier_solver.cpp for enhancements

---

## Command Reference

```bash
# Check build status
ls /fs1/home/ceoas/chenchon/mfem/mfem-src/build/libmfem.a

# Build solver
cd /fs1/home/ceoas/chenchon/mfem/2D-cylinder/build
cmake -DCMAKE_BUILD_TYPE=Release -DMFEM_DIR=../mfem-src ..
make -j4

# Run solver
./navier_solver -Re 1000 -dt 0.001 -t 100

# Analyze results
python3 ../plot_forces.py forces.dat

# View output
head forces.dat
ls -lh sol_*.gf

# Download results
scp -r chenchon@hpc:...2D-cylinder/build/* local_folder/
```

---

## Estimated Timeline

| Step | Duration |
|------|----------|
| MFEM build completion | 5-20 min (currently in progress) |
| Solver compilation | 2-5 min |
| Quick test simulation | 5-10 min |
| Analysis & plotting | 2-3 min |
| **Total to first results** | **15-40 minutes** |

---

## Key Physical Results to Look For

1. **Steady-state drag**: Should be ~1.2-1.3 for Re=1000
2. **Periodic lift oscillations**: Regular sinusoidal pattern
3. **Strouhal number**: Should be ~0.21-0.22
4. **Phase portrait**: Should form a closed loop after transients
5. **Frequency peak**: Spectral plot should show clear single peak

---

## Common Questions

**Q: How long does a full simulation take?**
A: ~30-60 minutes for 100 time units at Re=1000

**Q: Can I stop and restart?**
A: Not currently - would need checkpoint implementation

**Q: Can I run in parallel?**
A: Not yet - MPI support is planned for future versions

**Q: How much disk space?**
A: ~500 MB for typical simulation outputs

**Q: Can I change the mesh?**
A: Yes, edit `generate_mesh.py` and rerun CMake

---

## Help & Documentation

- **Detailed build**: `BUILD_AND_RUN_GUIDE.md`
- **Theory & physics**: `README.md`
- **Visualization**: `VISUALIZATION_GUIDE.md`
- **Project overview**: `PROJECT_SETUP_SUMMARY.md`

---

**Status**: Project ready, MFEM building, then ready to run!

Next action: Wait for MFEM completion, then build solver and run.

