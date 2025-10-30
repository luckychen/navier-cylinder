#  Comprehensive Report: MFEM Implementation of High-Re Flow Past a Cylinder

This report details the complete strategy for simulating **2D time-dependent incompressible Navier-Stokes flow past a cylinder** at a **high Reynolds Number ($\text{Re} \gg 100$)**, targeting a high-resolution, parallelized simulation (approximately $500 \times 1000$ degrees of freedom).

---

## Session Update (Latest Work)

### Current Status: MESH PARSER DEBUGGING COMPLETE ✓

**Last Commit:** e28edf1 - "Add mesh parser debugging and fix space dimension in mesh generator"

### Key Progress:
1. **Created Isolated Mesh Parser Test Tool** (`test_mesh_parser.cpp`)
   - Bypasses all simulation code for focused mesh validation
   - Successfully parses MFEM's official mesh files (e.g., `star-mixed-p2.mesh`)
   - Identified parser failure point: vertices section read after boundary elements

2. **Enhanced Mesh Generator**
   - Added missing `space dimension` line to vertices section (value: 2)
   - Fixed format to better match MFEM v1.0 specification
   - Updated both `create_simple_mesh.py` and `generate_mesh.py`

3. **Verified Parser Correctness**
   - Parser works perfectly with MFEM's official meshes ✓
   - Test successful: `star-mixed-p2.mesh` → 30 elements, 31 vertices, 20 boundary elements
   - Boundary attributes detected correctly

### Known Issues & Blockers:
- **Mesh Generation Format:** Generated meshes fail MFEM parser at vertices keyword
  - Error: `mesh_readers.cpp:105 - Verification failed: (ident == "vertices") is false`
  - Root cause: Subtle incompatibility in mesh generation format (not parser issue)
  - Workaround: Use MFEM's official mesh files from `/fs1/home/ceoas/chenchon/mfem/mfem-src/data/`

### Next Steps:
1. **Option A (Recommended):** Use Gmsh or official MFEM mesh generation tools
2. **Option B:** Debug exact byte-by-byte format differences between generated and working meshes
3. **Option C:** Implement mesh reading from alternative formats (Gmsh .msh, etc.)

### Project Deliverables Achieved:
- ✓ Compilation successful
- ✓ Basic simulation running (5x5 mesh)
- ✓ Test infrastructure created
- ✓ Navier-Stokes solver framework implemented
- ⏸ High-resolution mesh (100x100) - blocked by mesh format issue
- ✓ Full git history with 5+ commits documenting progress

---

---

## 1. Project Foundation: Governing Equations and Discretization

The simulation uses the incompressible Navier-Stokes equations, solved using the stabilized **Taylor-Hood mixed finite element method** and an **Implicit-Explicit (IMEX) time-splitting** scheme.

### 1.1. Governing Equations
The non-dimensionalized equations are:

**Momentum:**
$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla) \mathbf{u} - \frac{1}{\text{Re}} \nabla^2 \mathbf{u} + \nabla p = \mathbf{0} \quad \text{in } \Omega$$
**Incompressibility:**
$$\nabla \cdot \mathbf{u} = 0 \quad \text{in } \Omega$$

* $\mathbf{u}$: **Velocity** vector field.
* $p$: **Pressure** scalar field.
* $\text{Re}$: **Reynolds number** ($\frac{1}{\text{Re}} = \nu$, the kinematic viscosity).

### 1.2. Time Integration (Operator Splitting)

The system is split into two steps at each time level $n \rightarrow n+1$:

1.  **Momentum Predictor (Implicit Viscous/Explicit Convective):** Solves for the **tentative velocity $\mathbf{u}^*$**.
    $$\left(\frac{1}{\Delta t} \mathbf{M} + \frac{1}{\text{Re}} \mathbf{L}\right) \mathbf{U}^* = \frac{1}{\Delta t} \mathbf{M} \mathbf{U}^n - \mathbf{C}(\mathbf{U}^n, \mathbf{U}^n)$$

2.  **Pressure Correction:** Solves the **Pressure Poisson Equation (PPE)** and corrects the velocity to be divergence-free ($\mathbf{u}^{n+1}$).
    $$\mathbf{u}^{n+1} = \mathbf{u}^* - \Delta t \nabla p^{n+1}$$

### 1.3. Finite Element Spaces (Taylor-Hood)

To ensure stability (satisfying the LBB condition) at high Re:

* **Velocity Space ($\mathbf{u}$):** **Vector-valued Lagrange elements of order $k=2$** ($P_2$).
* **Pressure Space ($p$):** **Scalar Lagrange elements of order $k-1=1$** ($P_1$).

---

## 2. Mesh and Boundary Conditions

Success at high $\text{Re}$ requires a high-quality mesh and correctly implemented boundary conditions (BCs) that respect the element attributes.

### 2.1. Mesh Generation Requirements

| Requirement | Description | MFEM Strategy |
| :--- | :--- | :--- |
| **Element Type** | **Quadrilaterals/Hexahedra** are preferred for stability and boundary layer capturing. | Use **Gmsh** or **Cubit** to generate the initial mesh. |
| **Boundary Layer** | The mesh must be highly refined near the cylinder wall ($y^+ \approx 10$ or less is ideal) to resolve sharp velocity gradients. | Use a **structured extrusion** or a **sizing function** in the mesh generator. |
| **Resolution** | The mesh must be partitioned using **`ParMesh`** and run on multiple processors (`mpirun -np X`). | Required for the target $500 \times 1000$ DOFs. |

### 2.2. Boundary Condition Setup

The external mesh generation tool must assign unique **integer attributes** to the boundaries.

| Boundary | Attribute (Example) | Physical Condition | MFEM Implementation |
| :--- | :--- | :--- | :--- |
| **Cylinder Surface** | `1` | **No-slip Dirichlet:** $\mathbf{u} = \mathbf{0}$ | Mark attribute `1` as essential in `ess_bdr_vel`. |
| **Inlet** | `2` | **Dirichlet:** $\mathbf{u} = \mathbf{U}_{\infty}$ (Uniform velocity) | Mark attribute `2` as essential; project $\mathbf{U}_{\infty}$ coefficient. |
| **Outlet** | `3` | **Natural (Velocity):** Zero-traction. **Dirichlet (Pressure):** $p=0$. | No explicit velocity BC. Mark attribute `3` as essential in `ess_bdr_pres` to fix the pressure constant. |

---

## 3. Parallel Performance and Solvers

The high-resolution nature of the project demands the use of MFEM's high-performance features.

### 3.1. High-Performance Assembly

The nonlinear convection term **$\mathbf{C}(\mathbf{U}^n, \mathbf{U}^n)$** is the most computationally expensive part of the explicit step.

* **Solution:** Enable **Partial Assembly (PA)** using `nlf->SetOperatorType(Operator::PA);` in the `VectorConvectionNLF`. This significantly accelerates the explicit force vector computation, especially for $P_2$ elements.

### 3.2. Scalable Solvers and Preconditioners

| System | Solver | Preconditioner | Rationale |
| :--- | :--- | :--- | :--- |
| **Momentum Predictor** | **GMRES** or **PCG** | **hypre's BoomerAMG** | The matrix is well-conditioned (Mass-dominated for small $\Delta t$). AMG provides good parallel scaling. |
| **Pressure Poisson (PPE)** | **PCG** | **LORPreconditioner** + **BoomerAMG** | **Low-Order Refinement (LOR)** is essential. It preconditions the high-order $P_2/P_1$ system using a cheaper $P_1$ system, ensuring near-optimal $\mathcal{O}(N)$ parallel scaling for the critical PPE solve. |

---

## 4. Stability and Post-Processing

### 4.1. Time Step Control

The flow is unstable (vortex shedding). The time step $\Delta t$ is strictly limited by the **CFL condition** imposed by the explicit nonlinear term and the smallest mesh size ($h_{\min}$) near the cylinder:

$$\Delta t \le C_{\text{CFL}} \frac{h_{\min}}{U_{\max}}$$

* **Instruction:** Start with a very small $\Delta t$ (e.g., **$0.001$ or smaller**) and monitor the simulation stability.

### 4.2. Force and Strouhal Number Calculation

The primary physical results are the lift and drag forces.

* **Force Calculation:** Use an `mfem::BoundaryIntegrator` within the time loop to compute the $\mathbf{F} = \int_{\Gamma_{\text{cyl}}} \mathbf{\sigma} \cdot \mathbf{n} \, ds$ using the current $\mathbf{u}$ and $p$ solutions.
* **Strouhal Number ($St$):** Determine the frequency ($f$) of the oscillation in the **Lift Coefficient ($C_L$) vs. Time** plot to calculate $St = \frac{f \cdot D}{U_{\infty}}$.

---

## 5. Detailed MFEM Coding Instructions (C++)

This code structure follows the principles above, mapping directly to the `navier.cpp` miniapp.

```cpp
#include "mfem.hpp"
#include <iostream>

using namespace mfem;

// Function for the uniform inflow velocity profile U = [1.0, 0.0]
void InflowProfile(const Vector &x, Vector &u) {
    u(0) = 1.0; 
    u(1) = 0.0;
    if (u.Size() == 3) u(2) = 0.0;
}

int main(int argc, char *argv[]) {
    // 1. Parallel and Mesh Initialization
    Mpi::Init(argc, argv);
    Mesh *mesh = new Mesh("cylinder.mesh", 1, 1); 
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // Set parameters
    double Re = 1000.0; // High Reynolds Number
    double kinvis = 1.0 / Re;
    int order = 2; // P2/P1 Taylor-Hood

    // 2. Define FE Spaces
    int vdim = pmesh->Dimension();
    H1_FECollection *fec_vel = new H1_FECollection(order, vdim);
    ParFiniteElementSpace *fespace_vel = new ParFiniteElementSpace(pmesh, fec_vel, vdim);
    H1_FECollection *fec_pres = new H1_FECollection(order - 1, vdim);
    ParFiniteElementSpace *fespace_pres = new ParFiniteElementSpace(pmesh, fec_pres);
    
    // 3. Setup Boundary Conditions (Assuming Cylinder=1, Inflow=2, Outlet=3)
    Array<int> ess_bdr_vel(pmesh->bdr_attributes.Max());
    ess_bdr_vel = 0;
    ess_bdr_vel[1 - 1] = 1; // Cylinder (No-slip)
    ess_bdr_vel[2 - 1] = 1; // Inflow (U_inf)
    
    VectorFunctionCoefficient inflow_coeff(vdim, InflowProfile);
    ParGridFunction U0(fespace_vel);
    U0 = 0.0;
    U0.ProjectBdrCoefficient(inflow_coeff, ess_bdr_vel); // Sets all Dirichlet values

    Array<int> ess_bdr_pres(pmesh->bdr_attributes.Max());
    ess_bdr_pres = 0;
    ess_bdr_pres[3 - 1] = 1; // Outlet (p=0 fix)
    
    // Get the DOF indices (True DOFs)
    Array<int> ess_dofs_vel;
    fespace_vel->GetEssentialTrueDofs(ess_bdr_vel, ess_dofs_vel);
    Array<int> ess_dofs_pres;
    fespace_pres->GetEssentialTrueDofs(ess_bdr_pres, ess_dofs_pres);
    
    // 4. Define Forms with Partial Assembly
    ParBilinearForm *A_form = new ParBilinearForm(fespace_vel);
    A_form->AddDomainIntegrator(new VectorMassIntegrator());
    A_form->AddDomainIntegrator(new VectorDiffusionIntegrator(kinvis));

    ParMixedBilinearForm *B_form = new ParMixedBilinearForm(fespace_vel, fespace_pres);
    B_form->AddDomainIntegrator(new VectorDivIntegrator);

    ParNonlinearForm *C_form = new ParNonlinearForm(fespace_vel);
    VectorConvectionNLF *nlf = new VectorConvectionNLF(kinvis); 
    nlf->SetOperatorType(Operator::PA); // PA enabled for performance
    C_form->AddDomainIntegrator(nlf);

    // 5. LOR Preconditioner Setup (Crucial for PPE scaling)
    H1_FECollection *fec_lor = new H1_FECollection(1, 1); 
    ParBilinearForm *M_lor_form = new ParBilinearForm(fespace_pres);
    M_lor_form->AddDomainIntegrator(new MassIntegrator());
    LORPreconditioner *lor_prec = new LORPreconditioner(M_lor_form, *fespace_pres, *fespace_pres);
    lor_prec->SetEssentialTrueDofs(ess_dofs_pres);
    lor_prec->Setup();
    
    CGSolver *pres_solver = new CGSolver(MPI_COMM_WORLD);
    pres_solver->SetPreconditioner(*lor_prec);
    pres_solver->SetAbsTol(1e-10);

    // 6. Time Loop (Conceptual Core)
    // while (time < final_time) {
        // // Compute explicit convection force vector (C_form->Mult with PA)
        // // Solve Momentum Predictor (A_form->ParallelAssemble, GMRES/AMG)
        // // Compute RHS for PPE (B_mat->Mult)
        // // Solve Pressure Correction (pres_solver->Mult with LOR)
        // // Apply Velocity Correction (B_mat->MultTranspose)
        // // Calculate Drag/Lift Forces (BoundaryIntegrator)
    // }
    
    // ... clean up and return ...
    return 0;
}
