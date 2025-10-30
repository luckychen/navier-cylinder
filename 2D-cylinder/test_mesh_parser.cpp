#include "mfem.hpp"
#include <iostream>
#include <fstream>

using namespace std;
using namespace mfem;

int main(int argc, char *argv[]) {
    cout << "=== MFEM Mesh Parser Debug Tool ===" << endl;
    cout << "Testing mesh file parsing only (no simulation)" << endl << endl;

    string mesh_file = "cylinder.mesh";
    if (argc > 1) {
        mesh_file = argv[1];
    }

    cout << "Attempting to load mesh: " << mesh_file << endl;

    try {
        // Try to load mesh
        Mesh *mesh = new Mesh(mesh_file.c_str(), 1, 1);

        cout << "\n✓ SUCCESS: Mesh loaded successfully!" << endl;
        cout << "\nMesh Statistics:" << endl;
        cout << "  Dimensions: " << mesh->Dimension() << "D" << endl;
        cout << "  Elements: " << mesh->GetNE() << endl;
        cout << "  Vertices: " << mesh->GetNV() << endl;
        cout << "  Boundary Elements: " << mesh->GetNBE() << endl;
        cout << "  Edges: " << mesh->GetNEdges() << endl;

        // Check boundary attributes
        if (mesh->GetNBE() > 0) {
            cout << "\nBoundary Information:" << endl;
            int max_bdr_attr = mesh->bdr_attributes.Max();
            cout << "  Max boundary attribute: " << max_bdr_attr << endl;

            for (int i = 1; i <= max_bdr_attr; i++) {
                int count = 0;
                for (int j = 0; j < mesh->GetNBE(); j++) {
                    if (mesh->GetBdrAttribute(j) == i) count++;
                }
                if (count > 0) {
                    cout << "    Attribute " << i << ": " << count << " elements" << endl;
                }
            }
        }

        delete mesh;
        cout << "\n✓ All checks passed!" << endl;
        return 0;

    } catch (exception &e) {
        cerr << "\n✗ ERROR: Mesh parsing failed!" << endl;
        cerr << "Exception: " << e.what() << endl;
        return 1;
    }
}
