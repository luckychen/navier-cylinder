#!/usr/bin/env python3
"""Create a simple working 2D mesh for testing - based on MFEM v1.0 format."""

import math

# Create a simple rectangular mesh using triangles (easier for MFEM to handle)
nx, ny = 5, 5
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

# Create triangular elements (two triangles per quad)
elements = []
domain_id = 1

for j in range(ny):
    for i in range(nx):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i + 1, j)]
        v2 = vertex_map[(i + 1, j + 1)]
        v3 = vertex_map[(i, j + 1)]

        # Triangle 1
        elements.append([2, v0, v1, v2, domain_id])  # geom=2 (triangle), vertices, domain
        # Triangle 2
        elements.append([2, v0, v2, v3, domain_id])

# Boundary segments (1D line elements)
boundary_elems = []

# Left boundary (inlet) - attribute 2
for j in range(ny):
    v0 = vertex_map[(0, j)]
    v1 = vertex_map[(0, j + 1)]
    boundary_elems.append([1, v0, v1, 2])  # geom=1 (line), vertices, attribute

# Right boundary (outlet) - attribute 3
for j in range(ny):
    v0 = vertex_map[(nx, j)]
    v1 = vertex_map[(nx, j + 1)]
    boundary_elems.append([1, v0, v1, 3])

# Top boundary (wall) - attribute 4
for i in range(nx):
    v0 = vertex_map[(i, ny)]
    v1 = vertex_map[(i + 1, ny)]
    boundary_elems.append([1, v0, v1, 4])

# Bottom boundary (wall) - attribute 4
for i in range(nx):
    v0 = vertex_map[(i, 0)]
    v1 = vertex_map[(i + 1, 0)]
    boundary_elems.append([1, v1, v0, 4])  # Reversed orientation

# Write MFEM mesh v1.0
with open("cylinder.mesh", "w") as f:
    f.write("MFEM mesh v1.0\n\n")

    # Spatial dimension
    f.write("dimension\n2\n\n")

    # Elements
    f.write("elements\n")
    f.write(f"{len(elements)}\n")
    for elem in elements:
        # Format: attribute geom v0 v1 [v2 [v3]]
        if elem[0] == 2:  # Triangle: attribute geom v0 v1 v2
            f.write("{} {} {} {} {}\n".format(elem[4], elem[0], elem[1], elem[2], elem[3]))

    f.write("\n")

    # Boundary elements
    f.write("boundary\n")
    f.write(f"{len(boundary_elems)}\n")
    for belem in boundary_elems:
        # Format: geom v0 v1 [v2 [v3]] attribute
        f.write("{} {} {} {}\n".format(belem[0], belem[1], belem[2], belem[3]))

    f.write("\n")

    # Vertices
    f.write("vertices\n")
    f.write(f"{len(vertices)}\n")
    for v in vertices:
        f.write("{} {}\n".format(v[0], v[1]))

print(f"Created simple mesh: {len(vertices)} vertices, {len(elements)} elements, {len(boundary_elems)} boundary elements")
