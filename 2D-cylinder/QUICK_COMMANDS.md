# Quick Commands Reference

## Setup (One Time)
```bash
bash setup_environment.sh          # Install everything
```

## Daily Workflow
```bash
source activate.sh                 # Activate conda environment
bash quick_test.sh                 # Run example
```

## Run Simulations
```bash
# Default (100×100, Re=100, 0.5 sec)
./build/navier_simple -m cylinder_structured.mesh

# Custom Reynolds
./build/navier_simple -m cylinder_structured.mesh -Re 200

# Longer time
./build/navier_simple -m cylinder_structured.mesh -t 2.0

# All options
./build/navier_simple -h
```

## Generate Meshes
```bash
python3 generate_cylinder_mesh.py 50 50    # Small
python3 generate_cylinder_mesh.py 100 100  # Standard
python3 generate_cylinder_mesh.py 200 200  # Large
```

## Analyze Results
```bash
python3 analyze_results.py         # Generate plots
```

## Git Operations
```bash
git status                         # Check status
git add -A                         # Stage changes
git commit -m "message"            # Commit
git push origin main               # Push to GitHub
git log --oneline | head -10       # View history
```

## Building from Scratch
```bash
cd build
cmake .. -DMFEM_DIR=/path/to/mfem
make -j4
```

## Parallel Execution
```bash
mpirun -np 4 ./build/navier_simple -m cylinder_structured.mesh
mpirun -np 8 ./build/navier_simple -m cylinder_structured.mesh -t 2.0
```

## Useful Files
- **START_HERE.md** - Begin here (60 sec)
- **README.md** - Overview (2 min)
- **README_SETUP.md** - Full guide (10 min)
- **WORKFLOW.md** - Git guide (5 min)
- **navier_simple.cpp** - Source code

## Performance Tips
- Smaller mesh = faster: `python3 generate_cylinder_mesh.py 50 50`
- Larger time step = fewer iterations: `-dt 0.02`
- Parallel: `mpirun -np 8 ./build/navier_simple`

## GitHub URL
https://github.com/luckychen/navier-cylinder
