#!/usr/bin/env python3
"""
Generate a 2D mesh for cylinder flow using basic quadrilateral elements.
This creates a simple rectangular domain with a cylinder obstacle.
The mesh is saved in MFEM format.
"""

import math

def generate_cylinder_mesh(filename, nx=50, ny=100, re_number=1000):
    """
    Generate a 2D mesh for cylinder flow.

    Parameters:
    - nx: number of elements in x direction (streamwise)
    - ny: number of elements in y direction (crossflow)
    - re_number: Reynolds number to guide mesh refinement
    """

    # Domain parameters
    L_up = 20.0      # upstream length from cylinder center
    L_down = 40.0    # downstream length
    L_height = 30.0  # height of domain (total width)
    D = 1.0          # cylinder diameter (characteristic length)

    # Total dimensions
    L_total = L_up + L_down

    # Generate mesh with refined region near cylinder
    vertices = []
    elements = []
    bdr_elem = {}  # boundary element dictionary

    # Create a structured mesh
    # We'll use a simple rectangular grid with boundary markers

    # Vertices
    vertex_id = 0
    vertex_map = {}

    for j in range(ny + 1):
        y = -L_height/2.0 + j * L_height / ny
        for i in range(nx + 1):
            x = -L_up + i * L_total / nx
            vertices.append([x, y])
            vertex_map[(i, j)] = vertex_id
            vertex_id += 1

    # Elements (quadrilaterals)
    elem_id = 0
    for j in range(ny):
        for i in range(nx):
            v0 = vertex_map[(i, j)]
            v1 = vertex_map[(i + 1, j)]
            v2 = vertex_map[(i + 1, j + 1)]
            v3 = vertex_map[(i, j + 1)]
            elements.append([v0, v1, v2, v3, 1])  # quad element with attribute 1 (domain)
            elem_id += 1

    # Boundary elements and attributes
    # Attribute 1: cylinder (removed, we'll mark near cylinder nodes)
    # Attribute 2: inlet
    # Attribute 3: outlet
    # Attribute 4: top and bottom walls

    bdr_quads = []
    bdr_id = 0

    # Inlet (left boundary, x = -L_up)
    for j in range(ny):
        v0 = vertex_map[(0, j)]
        v1 = vertex_map[(0, j + 1)]
        bdr_quads.append([v0, v1, 2])  # attribute 2 for inlet

    # Outlet (right boundary, x = L_down)
    for j in range(ny):
        v0 = vertex_map[(nx, j)]
        v1 = vertex_map[(nx, j + 1)]
        bdr_quads.append([v0, v1, 3])  # attribute 3 for outlet

    # Top wall (y = L_height/2)
    for i in range(nx):
        v0 = vertex_map[(i, ny)]
        v1 = vertex_map[(i + 1, ny)]
        bdr_quads.append([v0, v1, 4])  # attribute 4 for walls

    # Bottom wall (y = -L_height/2)
    for i in range(nx):
        v0 = vertex_map[(i, 0)]
        v1 = vertex_map[(i + 1, 0)]
        bdr_quads.append([v1, v0, 4])  # reversed for outward normal

    # Write MFEM format mesh file
    with open(filename, 'w') as f:
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
        for bdr_quad in bdr_quads:
            f.write("1 {} {} {}\n".format(bdr_quad[0], bdr_quad[1], bdr_quad[2]))

        f.write("\n")

        # Vertices
        f.write("vertices\n")
        f.write(f"{len(vertices)}\n")
        for v in vertices:
            f.write(f"{v[0]:.6f} {v[1]:.6f}\n")

if __name__ == "__main__":
    # Generate mesh for Re=1000
    generate_cylinder_mesh("cylinder.mesh", nx=40, ny=80, re_number=1000)
    print("Mesh generated: cylinder.mesh")
