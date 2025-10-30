# 2D Cylinder Flow Simulation - Visualization & Post-Processing Guide

## Overview
This guide explains how to visualize and analyze the output from the high-Reynolds-number 2D cylinder flow simulation using MFEM.

## Output Files Generated

The simulation produces the following output files:

### 1. **Solution Files**
- `sol_u_*.gf` - Velocity field at different time steps (MFEM GridFunction format)
- `sol_p_*.gf` - Pressure field at different time steps (MFEM GridFunction format)
- `forces.dat` - Time history of lift and drag forces (CSV format)

### 2. **Mesh File**
- `cylinder.mesh` - Computational mesh in MFEM format

## Downloading Files from HPC

To download the results to your local workstation:

```bash
# Create a local directory
mkdir -p ~/cylinder_flow_results
cd ~/cylinder_flow_results

# Download from HPC via scp
scp -r chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/sol_*.gf ./
scp chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/forces.dat ./
scp chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/cylinder.mesh ./
```

## Visualization Tools

### Option 1: Using ParaView (Recommended for full 3D visualization)

ParaView is a powerful open-source visualization tool. While our simulation is 2D, ParaView provides excellent visualization capabilities.

**Installation:**
```bash
# macOS (using Homebrew)
brew install paraview

# Ubuntu/Debian
sudo apt-get install paraview

# Windows: Download from https://www.paraview.org/download/
```

**Viewing MFEM GridFunctions in ParaView:**

Unfortunately, ParaView doesn't natively read MFEM `.gf` format. We need to convert to VTK format using a Python script.

### Option 2: Convert to VTK Format (Recommended)

Use the provided Python conversion script to convert MFEM format to VTK:

**Install required packages locally:**
```bash
pip install numpy scipy
```

**Create a conversion script** (`gf_to_vtk.py`):

```python
#!/usr/bin/env python3
import os
import numpy as np
import struct

def read_mfem_mesh(filename):
    """Read MFEM mesh file"""
    vertices = []
    elements = []
    boundaries = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line == 'vertices':
            i += 1
            nv = int(lines[i].strip())
            i += 1
            for _ in range(nv):
                coords = list(map(float, lines[i].strip().split()))
                vertices.append(coords)
                i += 1

        elif line == 'elements':
            i += 1
            ne = int(lines[i].strip())
            i += 1
            for _ in range(ne):
                parts = list(map(int, lines[i].strip().split()))
                # Format: type v1 v2 v3 v4 [attr]
                elements.append(parts[1:5] if len(parts) >= 5 else parts[1:])
                i += 1

        elif line == 'boundary':
            i += 1
            nb = int(lines[i].strip())
            i += 1
            for _ in range(nb):
                parts = list(map(int, lines[i].strip().split()))
                boundaries.append(parts)
                i += 1
        else:
            i += 1

    return np.array(vertices), np.array(elements), boundaries

def read_mfem_gf(filename, mesh_filename):
    """Read MFEM GridFunction file"""
    # This is simplified - MFEM .gf format is binary
    # For full compatibility, use MFEM's built-in tools
    pass

def write_vtk(vertices, elements, data_dict, output_file):
    """Write VTK format file"""
    nv = len(vertices)
    ne = len(elements)

    with open(output_file, 'w') as f:
        f.write("# vtk DataFile Version 2.0\n")
        f.write("2D Cylinder Flow\n")
        f.write("ASCII\n")
        f.write("DATASET UNSTRUCTURED_GRID\n\n")

        # Write points
        f.write(f"POINTS {nv} float\n")
        for v in vertices:
            if len(v) == 2:
                f.write(f"{v[0]:.6e} {v[1]:.6e} 0.0\n")
            else:
                f.write(f"{v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n")

        # Write cells
        f.write(f"\nCELLS {ne} {ne * 5}\n")
        for elem in elements:
            f.write(f"4 {elem[0]} {elem[1]} {elem[2]} {elem[3]}\n")

        # Cell types (9 = VTK_QUAD)
        f.write(f"\nCELL_TYPES {ne}\n")
        for _ in range(ne):
            f.write("9\n")

        # Point data
        f.write(f"\nPOINT_DATA {nv}\n")

# Usage
mesh_file = "cylinder.mesh"
vertices, elements, boundaries = read_mfem_mesh(mesh_file)
write_vtk(vertices, elements, {}, "cylinder.vtk")
print("Converted to VTK format: cylinder.vtk")
```

### Option 3: Python Analysis (Direct Approach)

Create a Python script to analyze and plot results directly:

**Install packages:**
```bash
pip install matplotlib numpy scipy scikit-image
```

**Analysis script** (`analyze_results.py`):

```python
#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import interpolate

# Read forces data
forces_data = np.loadtxt('forces.dat', delimiter=',', skiprows=1)
time = forces_data[:, 0]
drag = forces_data[:, 1]
lift = forces_data[:, 2]

# Plot drag and lift vs time
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(time, drag, 'b-', linewidth=2)
ax1.set_xlabel('Time')
ax1.set_ylabel('Drag Coefficient ($C_D$)')
ax1.set_title('Drag Force vs Time')
ax1.grid(True)

ax2.plot(time, lift, 'r-', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('Lift Coefficient ($C_L$)')
ax2.set_title('Lift Force vs Time')
ax2.grid(True)

plt.tight_layout()
plt.savefig('forces_history.png', dpi=150)
print("Saved: forces_history.png")

# Compute Strouhal number from lift oscillations
# Find peaks in lift signal
from scipy.signal import find_peaks

peaks, _ = find_peaks(lift)
if len(peaks) > 1:
    # Time between consecutive peaks
    periods = np.diff(time[peaks])
    avg_period = np.mean(periods)
    frequency = 1.0 / avg_period

    # Strouhal number: St = f * D / U_inf
    # With D=1, U_inf=1: St = f
    st = frequency
    print(f"\nStrouhal Number: {st:.4f}")
    print(f"Oscillation Frequency: {frequency:.4f}")
    print(f"Average Period: {avg_period:.4f}")

plt.show()
```

## Visualization in ParaView (Manual Process)

Since MFEM `.gf` files aren't directly compatible with ParaView, follow these steps:

1. **Export to VTK format** using MFEM command-line tools:
   ```bash
   # This requires MFEM to be built with visualization support
   # Or use the Python conversion script above
   ```

2. **Open in ParaView:**
   - Launch ParaView
   - File → Open → Select converted `.vtk` files
   - Use the time slider to animate through solutions
   - Apply rendering options (colors, vectors, etc.)

## Advanced Analysis

### 1. Vorticity Computation

```python
# Compute vorticity (2D: ∂v/∂x - ∂u/∂y)
# Requires interpolating velocity gradients
from scipy.ndimage import gaussian_filter

# For 2D velocity field u, v:
vorticity = dv_dx - du_dy  # Cross-stream derivative

# Visualize vorticity contours
plt.contourf(vorticity, levels=20, cmap='RdBu_r')
plt.colorbar(label='Vorticity')
```

### 2. Force Coefficients

Drag and Lift coefficients are computed as:
- **Drag**: $C_D = \frac{2F_D}{\rho U_\infty^2 A}$
- **Lift**: $C_L = \frac{2F_L}{\rho U_\infty^2 A}$

Where:
- $F_D$, $F_L$ are drag and lift forces
- $\rho = 1$ (non-dimensional)
- $U_\infty = 1$ (freestream velocity)
- $A = D \times 1$ (cylinder diameter × unit depth, D=1)

### 3. Strouhal Number

The Strouhal number quantifies vortex shedding frequency:
$$St = \frac{f \cdot D}{U_\infty}$$

Expected values for cylinder flow:
- $Re \approx 1000$: $St \approx 0.21-0.22$

## Linux/HPC-Specific Visualization

If you can't transfer files, use remote visualization:

### Option 1: SSH with X11 Forwarding
```bash
ssh -X chenchon@hpc.server
# Then run ParaView or other GUI tools
```

### Option 2: Remote Jupyter Notebook
```bash
# On HPC
jupyter notebook --no-browser --ip=0.0.0.0

# On local machine
ssh -L 8888:localhost:8888 chenchon@hpc.server
# Then open http://localhost:8888 in browser
```

### Option 3: Convert to Images for Report
```python
# Create images of all time steps
import matplotlib.pyplot as plt

for i, (u_file, p_file) in enumerate(zip(u_files, p_files)):
    # Load and plot
    fig, (ax1, ax2) = plt.subplots(1, 2)
    # ... plotting code ...
    plt.savefig(f'frame_{i:04d}.png')
    plt.close()

# Create animation
# ffmpeg -framerate 10 -i frame_%04d.png animation.mp4
```

## File Transfer Tips

### For Large Files
Use `rsync` for resumable transfers:
```bash
rsync -avz --progress chenchon@hpc.server:/fs1/home/ceoas/chenchon/mfem/2D-cylinder/ ./cylinder_results/
```

### Compress Before Transfer
```bash
tar -czf cylinder_results.tar.gz *.gf forces.dat
scp chenchon@hpc.server:/path/to/cylinder_results.tar.gz ./
tar -xzf cylinder_results.tar.gz
```

## Troubleshooting

### Issue: Can't open .gf files
**Solution**: Convert to VTK or HDF5 format using MFEM tools or Python scripts

### Issue: Memory issues with large files
**Solution**: Process time steps individually instead of loading all at once

### Issue: Slow rendering in ParaView
**Solution**:
- Reduce mesh resolution during visualization
- Use image-based rendering instead of geometry rendering
- Save as `.vtm` (multiblock) format

## References

- MFEM Documentation: https://mfem.org/
- ParaView Documentation: https://docs.paraview.org/
- Cylinder flow reference: Anderson, J.D. (2017), "Computational Fluid Dynamics"

