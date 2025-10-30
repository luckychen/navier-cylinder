#!/usr/bin/env python3
"""Create a simple working 2D mesh for testing."""

import math

# Create a simple rectangular mesh
nx, ny = 10, 10
Lx, Ly = 10.0, 5.0

vertices = []
vertex_id = 0
vertex_map = {}

# Create vertices
for j in range(ny + 1):
    y = -Ly/2 + j * Ly / ny
    for i in range(nx + 1):
        x = -Lx/2 + i * Lx / nx
        vertices.append([x, y])
        vertex_map[(i, j)] = vertex_id
        vertex_id += 1

# Create quadrilateral elements
elements = []
for j in range(ny):
    for i in range(nx):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i + 1, j)]
        v2 = vertex_map[(i + 1, j + 1)]
        v3 = vertex_map[(i, j + 1)]
        elements.append([v0, v1, v2, v3, 1])

# Boundary quads
bdr_quads = []

# Left boundary (inlet)
for j in range(ny):
    v0 = vertex_map[(0, j)]
    v1 = vertex_map[(0, j + 1)]
    bdr_quads.append([v0, v1, 2])

# Right boundary (outlet)
for j in range(ny):
    v0 = vertex_map[(nx, j)]
    v1 = vertex_map[(nx, j + 1)]
    bdr_quads.append([v0, v1, 3])

# Top boundary (wall)
for i in range(nx):
    v0 = vertex_map[(i, ny)]
    v1 = vertex_map[(i + 1, ny)]
    bdr_quads.append([v0, v1, 4])

# Bottom boundary (wall)
for i in range(nx):
    v0 = vertex_map[(i, 0)]
    v1 = vertex_map[(i + 1, 0)]
    bdr_quads.append([v1, v0, 4])

# Write MFEM mesh
with open("cylinder.mesh", "w") as f:
    f.write("MFEM mesh v1.0\n\n")

    # Spatial dimension
    f.write("dimension\n2\n\n")

    # Elements (quadrilaterals)
    f.write("elements\n")
    f.write(f"{len(elements)}\n")
    for elem in elements:
        f.write("1 {} {} {} {} {}\n".format(elem[0], elem[1], elem[2], elem[3], elem[4]))

    f.write("\n")

    # Boundary elements
    f.write("boundary\n")
    f.write(f"{len(bdr_quads)}\n")
    for bdr in bdr_quads:
        f.write("1 {} {} {}\n".format(bdr[0], bdr[1], bdr[2]))

    f.write("\n")

    # Vertices
    f.write("vertices\n")
    f.write(f"{len(vertices)}\n")
    for v in vertices:
        f.write("{} {}\n".format(v[0], v[1]))

print(f"Created simple mesh: {len(vertices)} vertices, {len(elements)} elements, {len(bdr_quads)} boundary elements")
