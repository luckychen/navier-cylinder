#!/usr/bin/env python3
"""
Analyze and plot results from the cylinder flow simulation
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import signal

def load_forces(filename):
    """Load force data from file"""
    try:
        data = np.loadtxt(filename)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        return data[:, 0], data[:, 1], data[:, 2]  # time, Cd, Cl
    except:
        print(f"Warning: Could not load {filename}")
        return None, None, None

def analyze_forces(time, Cd, Cl):
    """Analyze force coefficients"""
    if time is None:
        return {}

    # Calculate statistics
    Cd_mean = np.mean(Cd)
    Cd_std = np.std(Cd)
    Cl_mean = np.mean(Cl)
    Cl_std = np.std(Cl)
    Cl_amp = np.max(np.abs(Cl))

    # Try to find Strouhal number (frequency of oscillation)
    if len(time) > 10:
        dt = time[1] - time[0]
        # Compute FFT of lift coefficient
        fft_Cl = np.fft.fft(Cl - Cl_mean)
        freqs = np.fft.fftfreq(len(Cl), dt)

        # Find dominant frequency (exclude DC component)
        positive_freqs = freqs[1:len(freqs)//2]
        positive_fft = np.abs(fft_Cl[1:len(fft_Cl)//2])

        if len(positive_fft) > 0:
            peak_idx = np.argmax(positive_fft)
            dominant_freq = positive_freqs[peak_idx]
            # Strouhal number = f * D / U_inf (D=1, U_inf=1)
            St = dominant_freq
        else:
            St = 0.0
    else:
        St = 0.0

    return {
        'Cd_mean': Cd_mean,
        'Cd_std': Cd_std,
        'Cl_mean': Cl_mean,
        'Cl_std': Cl_std,
        'Cl_amp': Cl_amp,
        'St': St
    }

def plot_forces(time, Cd, Cl, title_suffix=""):
    """Plot force coefficients vs time"""
    if time is None:
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Plot drag coefficient
    ax1.plot(time, Cd, 'b-', linewidth=1.5)
    ax1.set_ylabel('Drag Coefficient $C_D$', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f'Force Coefficients vs Time{title_suffix}', fontsize=14)

    # Plot lift coefficient
    ax2.plot(time, Cl, 'r-', linewidth=1.5)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Lift Coefficient $C_L$', fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig

def main():
    """Main analysis routine"""
    print("=" * 60)
    print("Cylinder Flow Simulation Results Analysis")
    print("=" * 60)

    # Check for available force files
    force_files = [f for f in os.listdir('.') if f.startswith('forces_') and f.endswith('.dat')]

    if not force_files:
        print("No force files found. Run simulation first.")
        return

    print(f"\nFound {len(force_files)} force file(s):")
    for f in force_files:
        print(f"  - {f}")

    # Analyze each file
    results = {}
    for filename in force_files:
        print(f"\n{'-'*40}")
        print(f"Analyzing: {filename}")
        print(f"{'-'*40}")

        time, Cd, Cl = load_forces(filename)
        if time is not None:
            stats = analyze_forces(time, Cd, Cl)
            results[filename] = stats

            print(f"  Time range: {time[0]:.3f} to {time[-1]:.3f} s")
            print(f"  Number of samples: {len(time)}")
            print(f"  Drag coefficient:")
            print(f"    Mean: {stats['Cd_mean']:.6f}")
            print(f"    Std:  {stats['Cd_std']:.6f}")
            print(f"  Lift coefficient:")
            print(f"    Mean: {stats['Cl_mean']:.6f}")
            print(f"    Std:  {stats['Cl_std']:.6f}")
            print(f"    Amplitude: {stats['Cl_amp']:.6f}")
            print(f"  Strouhal number: {stats['St']:.4f}")

            # Create plot
            suffix = f" ({filename.replace('forces_', '').replace('.dat', '')})"
            fig = plot_forces(time, Cd, Cl, suffix)

            # Save plot
            plot_name = filename.replace('.dat', '.png')
            fig.savefig(plot_name, dpi=150, bbox_inches='tight')
            print(f"  Saved plot: {plot_name}")
            plt.close()

    # Compare results if multiple files
    if len(results) > 1:
        print(f"\n{'='*60}")
        print("Comparison of Results")
        print(f"{'='*60}")
        print(f"{'File':<20} {'Cd_mean':<10} {'Cl_amp':<10} {'St':<10}")
        print(f"{'-'*50}")
        for fname, stats in results.items():
            name = fname.replace('forces_', '').replace('.dat', '')
            print(f"{name:<20} {stats['Cd_mean']:<10.6f} {stats['Cl_amp']:<10.6f} {stats['St']:<10.4f}")

    # Physical validation
    print(f"\n{'='*60}")
    print("Physical Validation (Re=100)")
    print(f"{'='*60}")
    print("Expected values from literature:")
    print("  Cd_mean: ~1.2-1.4 (after fully developed)")
    print("  St: ~0.16-0.18")
    print("\nNote: Current implementation is simplified.")
    print("Full nonlinear convection term needed for accurate results.")

    print(f"\n{'='*60}")
    print("Analysis Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()