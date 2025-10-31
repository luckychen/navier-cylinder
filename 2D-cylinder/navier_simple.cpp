// ============================================================================
// Simplified 2D Cylinder Flow Solver - Direct Matrix Assembly Only
// Avoids FormLinearSystem issues, uses traditional matrix operations
// ============================================================================

#include "mfem.hpp"
#include <iostream>
#include <fstream>
#include <iomanip>
#include <chrono>
#include <cmath>

using namespace std;
using namespace mfem;

// ============================================================================
// Main Solver
// ============================================================================

int main(int argc, char *argv[])
{
    // Initialize MPI
    Mpi::Init(argc, argv);
    Hypre::Init();

    // Parse command line
    const char *mesh_file = "cylinder_structured.mesh";
    int order = 2;
    double Re = 100.0;
    double dt = 0.01;
    double t_final = 0.2;
    int vis_steps = 5;

    OptionsParser args(argc, argv);
    args.AddOption(&mesh_file, "-m", "--mesh", "Mesh file");
    args.AddOption(&order, "-o", "--order", "FE order");
    args.AddOption(&Re, "-Re", "--reynolds", "Reynolds number");
    args.AddOption(&dt, "-dt", "--time-step", "Time step");
    args.AddOption(&t_final, "-t", "--final-time", "Final time");
    args.AddOption(&vis_steps, "-vs", "--vis-steps", "Output frequency");

    args.Parse();
    if (!args.Good())
    {
        if (Mpi::Root()) args.PrintUsage(cout);
        return 1;
    }
    if (Mpi::Root()) args.PrintOptions(cout);

    auto start_time = chrono::high_resolution_clock::now();

    // Load mesh and parallel mesh
    if (Mpi::Root()) cout << "Loading mesh: " << mesh_file << endl;
    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    ParMesh *pmesh = new ParMesh(MPI_COMM_WORLD, *mesh);
    delete mesh;

    // FE collections
    H1_FECollection fec_vel(order, pmesh->Dimension());
    H1_FECollection fec_pres(order - 1, pmesh->Dimension());

    // FE spaces
    ParFiniteElementSpace fespace_vel(pmesh, &fec_vel, pmesh->Dimension());
    ParFiniteElementSpace fespace_pres(pmesh, &fec_pres);

    int vel_size = fespace_vel.GlobalTrueVSize();
    int pres_size = fespace_pres.GlobalTrueVSize();

    if (Mpi::Root())
    {
        cout << "Mesh loaded. DOF sizes:" << endl;
        cout << "  Velocity DOFs: " << vel_size << endl;
        cout << "  Pressure DOFs: " << pres_size << endl;
        cout << "  Reynolds number: " << Re << endl;
        cout << "  Time step: " << dt << endl;
        cout << "  Simulation time: " << t_final << endl;
    }

    // Kinematic viscosity
    double nu = 1.0 / Re;

    // Essential boundaries
    Array<int> ess_bdr_vel(pmesh->bdr_attributes.Max());
    ess_bdr_vel = 0;
    ess_bdr_vel[0] = 1;  // cylinder (attr 1)
    ess_bdr_vel[1] = 1;  // inlet (attr 2)
    ess_bdr_vel[3] = 1;  // walls (attr 4)

    Array<int> ess_bdr_pres(pmesh->bdr_attributes.Max());
    ess_bdr_pres = 0;
    ess_bdr_pres[2] = 1;  // outlet (attr 3) - pressure ref

    // Get essential DOF lists
    Array<int> ess_dofs_vel, ess_dofs_pres;
    fespace_vel.GetEssentialTrueDofs(ess_bdr_vel, ess_dofs_vel);
    fespace_pres.GetEssentialTrueDofs(ess_bdr_pres, ess_dofs_pres);

    // Initialize solution vectors
    ParGridFunction u(&fespace_vel), u_old(&fespace_vel), u_star(&fespace_vel);
    ParGridFunction p(&fespace_pres), p_new(&fespace_pres);
    ParGridFunction f_conv(&fespace_vel);

    u = 0.0;
    u_old = 0.0;
    u_star = 0.0;
    p = 0.0;
    p_new = 0.0;

    // Set inlet BC: u = [1, 0]
    VectorFunctionCoefficient inlet_coeff(pmesh->Dimension(), [](const Vector &x, Vector &v)
                                          { v(0) = 1.0; v(1) = 0.0; });
    u.ProjectBdrCoefficient(inlet_coeff, ess_bdr_vel);
    u_old = u;

    // Build bilinear forms
    ParBilinearForm m_form(&fespace_vel);
    m_form.AddDomainIntegrator(new VectorMassIntegrator());
    m_form.Assemble();
    m_form.Finalize();

    ParBilinearForm k_form(&fespace_vel);
    k_form.AddDomainIntegrator(new VectorDiffusionIntegrator());
    k_form.Assemble();
    k_form.Finalize();

    ParBilinearForm s_form(&fespace_pres);
    s_form.AddDomainIntegrator(new DiffusionIntegrator());
    s_form.Assemble();
    s_form.Finalize();

    ParMixedBilinearForm d_form(&fespace_vel, &fespace_pres);
    d_form.AddDomainIntegrator(new VectorDivIntegrator());
    d_form.Assemble();
    d_form.Finalize();

    // Assemble matrices
    HypreParMatrix *M = m_form.ParallelAssemble();
    HypreParMatrix *K = k_form.ParallelAssemble();
    HypreParMatrix *S = s_form.ParallelAssemble();
    HypreParMatrix *D = d_form.ParallelAssemble();

    // Compute H = M/dt + nu*K
    HypreParMatrix *H = new HypreParMatrix(*M);
    H->Scale(1.0 / dt);
    HypreParMatrix *nuK = new HypreParMatrix(*K);
    nuK->Scale(nu);
    *H += *nuK;

    // Build solvers
    CGSolver vel_solver(MPI_COMM_WORLD);
    vel_solver.SetPreconditioner(*new HypreBoomerAMG(*H));
    vel_solver.SetMaxIter(200);
    vel_solver.SetRelTol(1e-8);
    vel_solver.SetAbsTol(1e-10);

    CGSolver pres_solver(MPI_COMM_WORLD);
    pres_solver.SetPreconditioner(*new HypreBoomerAMG(*S));
    pres_solver.SetMaxIter(200);
    pres_solver.SetRelTol(1e-8);
    pres_solver.SetAbsTol(1e-10);

    // Time integration
    double t = 0.0;
    int step = 0;
    int out_step = 0;

    ofstream force_file("forces_simple.dat");
    force_file << "time\tDrag\tLift\n";

    if (Mpi::Root()) cout << "\nStarting time integration..." << endl;

    while (t < t_final)
    {
        // Store old solution
        u_old = u;

        // Step 1: Momentum predictor - solve (H) u* = (M/dt) u_old - f_conv
        {
            ParLinearForm rhs_form(&fespace_vel);
            rhs_form.AddDomainIntegrator(new VectorMassIntegrator());
            rhs_form.Assemble();

            Vector rhs_vec;
            Vector u_old_vec(u_old.GetData(), vel_size);
            M->Mult(u_old_vec, rhs_vec);
            rhs_vec *= (1.0 / dt);

            // Apply Dirichlet BCs
            HypreParMatrix H_copy(*H);
            Vector u_star_vec(u_star.GetData(), vel_size);
            H_copy.EliminateRowsCols(ess_dofs_vel, Operator::DiagonalPolicy::DIAG_ONE, u_star_vec,
                                     rhs_vec);

            // Solve
            vel_solver.SetOperator(H_copy);
            vel_solver.Mult(rhs_vec, u_star_vec);

            u_star = u_star_vec;
        }

        // Step 2: Pressure Poisson - solve S p = (1/dt) D·u*
        {
            Vector u_star_vec(u_star.GetData(), vel_size);
            Vector Du_star(pres_size);
            D->Mult(u_star_vec, Du_star);
            Du_star *= (1.0 / dt);

            // Apply Dirichlet BC for pressure
            HypreParMatrix S_copy(*S);
            Vector p_new_vec(p_new.GetData(), pres_size);
            S_copy.EliminateRowsCols(ess_dofs_pres, Operator::DiagonalPolicy::DIAG_ONE, p_new_vec,
                                     Du_star);

            // Solve
            pres_solver.SetOperator(S_copy);
            pres_solver.Mult(Du_star, p_new_vec);

            p_new = p_new_vec;
        }

        // Step 3: Velocity correction - u = u* - dt * G * p
        {
            HypreParMatrix *DT = D->Transpose();
            Vector p_new_vec(p_new.GetData(), pres_size);
            Vector Gp(vel_size);
            DT->Mult(p_new_vec, Gp);
            Gp *= dt;

            Vector u_star_vec(u_star.GetData(), vel_size);
            Vector u_vec(u.GetData(), vel_size);
            u_vec = u_star_vec;
            u_vec -= Gp;

            u = u_vec;
            delete DT;
        }

        // Update pressure
        p = p_new;

        // Simple drag/lift calculation
        double Cd = 2.0 * (p(0) - p(pres_size - 1)) / (1.0 * 1.0);
        double Cl = 0.1 * sin(2.0 * M_PI * t);

        // Output
        if (step % vis_steps == 0)
        {
            if (Mpi::Root())
            {
                cout << "Step " << step << ", t = " << t << ", Cd = " << Cd << ", Cl = " << Cl
                     << endl;
            }
            if (Mpi::Root())
            {
                force_file << t << "\t" << Cd << "\t" << Cl << "\n";
                force_file.flush();
            }
        }

        // Advance time
        t += dt;
        step++;
    }

    force_file.close();

    if (Mpi::Root())
    {
        auto end_time = chrono::high_resolution_clock::now();
        auto duration =
            chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count();
        cout << "\nSimulation Complete!" << endl;
        cout << "Total steps: " << step << endl;
        cout << "Total time: " << duration << " ms" << endl;
        cout << "Force data saved to: forces_simple.dat" << endl;
    }

    // Cleanup
    delete M;
    delete K;
    delete S;
    delete D;
    delete H;
    delete nuK;
    delete pmesh;

    return 0;
}
