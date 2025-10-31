#!/usr/bin/env python3
"""
Generate a structured quadrilateral mesh for 2D flow past a cylinder
with proper MFEM v1.0 format and boundary attributes.

Domain: Rectangular channel with circular hole (cylinder)
Boundary attributes:
  1 = Cylinder surface (no-slip wall)
  2 = Inlet (left)
  3 = Outlet (right)
  4 = Top/Bottom walls (slip or periodic)
"""

import sys
import numpy as np

def generate_cylinder_mesh(nx=40, ny=20, radius=0.5,
                           domain_x=(-5.0, 15.0), domain_y=(-5.0, 5.0),
                           cylinder_center=(0.0, 0.0), output_file="cylinder.mesh"):
    """
    Generate structured quad mesh around a cylinder.

    For simplicity, we'll create a rectangular mesh with refined regions,
    then mark elements/boundaries appropriately.

    Strategy: Create a rectangular structured mesh, identify and mark
    cylinder boundary nodes, create boundary attributes.
    """

    # Domain bounds
    x_min, x_max = domain_x
    y_min, y_max = domain_y
    cx, cy = cylinder_center

    # Generate structured grid
    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)

    # Create vertex list
    vertices = []
    vertex_map = {}  # (i,j) -> vertex_id
    vertex_id = 0

    for j in range(ny):
        for i in range(nx):
            xi, yj = x[i], y[j]
            vertices.append((xi, yj))
            vertex_map[(i, j)] = vertex_id
            vertex_id += 1

    # Create elements (quadrilaterals)
    # Element type 3 = SQUARE (quad)
    # Vertex ordering: counter-clockwise
    elements = []
    elem_attribute = 1  # Default material attribute

    for j in range(ny - 1):
        for i in range(nx - 1):
            v0 = vertex_map[(i, j)]
            v1 = vertex_map[(i+1, j)]
            v2 = vertex_map[(i+1, j+1)]
            v3 = vertex_map[(i, j+1)]

            # Check if element contains cylinder (skip if inside)
            x_center = (x[i] + x[i+1]) / 2
            y_center = (y[j] + y[j+1]) / 2
            dist = np.sqrt((x_center - cx)**2 + (y_center - cy)**2)

            # Only add element if it's outside cylinder
            if dist > radius * 0.5:  # Threshold for element inclusion
                elements.append((elem_attribute, 3, v0, v1, v2, v3))

    # Create boundary elements
    # Boundary type 1 = SEGMENT
    boundary_elements = []

    # Bottom boundary (attribute 4 = walls)
    j = 0
    for i in range(nx - 1):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i+1, j)]
        boundary_elements.append((4, 1, v0, v1))

    # Right boundary (attribute 3 = outlet)
    i = nx - 1
    for j in range(ny - 1):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i, j+1)]
        boundary_elements.append((3, 1, v0, v1))

    # Top boundary (attribute 4 = walls)
    j = ny - 1
    for i in range(nx - 1, 0, -1):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i-1, j)]
        boundary_elements.append((4, 1, v0, v1))

    # Left boundary (attribute 2 = inlet)
    i = 0
    for j in range(ny - 1, 0, -1):
        v0 = vertex_map[(i, j)]
        v1 = vertex_map[(i, j-1)]
        boundary_elements.append((2, 1, v0, v1))

    # Cylinder boundary (attribute 1 = cylinder wall)
    # For now, approximate with vertices near cylinder
    for j in range(1, ny - 1):
        for i in range(1, nx - 1):
            xi, yj = x[i], y[j]
            dist = np.sqrt((xi - cx)**2 + (yj - cy)**2)

            # If vertex is near cylinder surface, check neighbors
            if abs(dist - radius) < (x[1] - x[0]) * 1.5:
                # Check if this is a boundary (has exterior neighbor)
                v_center = vertex_map[(i, j)]

                # Check each direction
                for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < nx and 0 <= nj < ny:
                        xi_n, yj_n = x[ni], y[nj]
                        dist_n = np.sqrt((xi_n - cx)**2 + (yj_n - cy)**2)

                        # If neighbor is inside cylinder, this is boundary edge
                        if dist_n < radius * 0.8 and dist > radius * 0.8:
                            v_neighbor = vertex_map[(ni, nj)]
                            # Add boundary segment
                            boundary_elements.append((1, 1, v_center, v_neighbor))

    # Write MFEM mesh file
    with open(output_file, 'w') as f:
        f.write("MFEM mesh v1.0\n")
        f.write("\n")

        # Dimension
        f.write("dimension\n")
        f.write("2\n")
        f.write("\n")

        # Elements
        f.write("elements\n")
        f.write(f"{len(elements)}\n")
        for elem in elements:
            f.write(" ".join(map(str, elem)) + "\n")
        f.write("\n")

        # Boundary elements
        f.write("boundary\n")
        f.write(f"{len(boundary_elements)}\n")
        for belem in boundary_elements:
            f.write(" ".join(map(str, belem)) + "\n")
        f.write("\n")

        # Vertices
        f.write("vertices\n")
        f.write(f"{len(vertices)}\n")
        f.write("2\n")  # Space dimension
        for v in vertices:
            f.write(f"{v[0]} {v[1]}\n")

    print(f"✓ Mesh generated: {output_file}")
    print(f"  Vertices: {len(vertices)}")
    print(f"  Elements: {len(elements)}")
    print(f"  Boundary elements: {len(boundary_elements)}")
    print(f"  Domain: x=[{x_min}, {x_max}], y=[{y_min}, {y_max}]")
    print(f"  Cylinder: center=({cx}, {cy}), radius={radius}")

if __name__ == "__main__":
    # Start with modest resolution for testing
    if len(sys.argv) > 1:
        nx = int(sys.argv[1])
        ny = int(sys.argv[2]) if len(sys.argv) > 2 else nx // 2
    else:
        nx = 60  # Reduced from 100
        ny = 30  # Reduced from 100

    generate_cylinder_mesh(
        nx=nx,
        ny=ny,
        radius=0.5,
        domain_x=(-5.0, 15.0),
        domain_y=(-5.0, 5.0),
        cylinder_center=(0.0, 0.0),
        output_file="cylinder_structured.mesh"
    )
