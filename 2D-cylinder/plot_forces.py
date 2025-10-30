#!/usr/bin/env python3
"""
Post-processing script to analyze drag/lift forces and vortex shedding
from cylinder flow simulation.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, welch
import os
import sys

def load_forces(filename):
    """Load force data from CSV file"""
    try:
        data = np.loadtxt(filename, delimiter=',', skiprows=1)
        if len(data.shape) == 1:
            data = data.reshape(1, -1)
        time = data[:, 0]
        drag = data[:, 1]
        lift = data[:, 2]
        return time, drag, lift
    except Exception as e:
        print(f"Error loading forces from {filename}: {e}")
        return None, None, None

def plot_forces(time, drag, lift, output_file='forces_history.png'):
    """Create figure showing drag and lift vs time"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Time series plots
    ax = axes[0, 0]
    ax.plot(time, drag, 'b-', linewidth=2, label='Drag')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Drag Coefficient ($C_D$)', fontsize=11)
    ax.set_title('Drag Force vs Time', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    ax = axes[0, 1]
    ax.plot(time, lift, 'r-', linewidth=2, label='Lift')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Lift Coefficient ($C_L$)', fontsize=11)
    ax.set_title('Lift Force vs Time', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Phase portrait (drag vs lift)
    ax = axes[1, 0]
    ax.plot(drag, lift, 'g-', linewidth=1, alpha=0.7)
    ax.scatter(drag[0], lift[0], color='green', s=100, marker='o', label='Start')
    ax.scatter(drag[-1], lift[-1], color='red', s=100, marker='x', label='End')
    ax.set_xlabel('Drag Coefficient ($C_D$)', fontsize=11)
    ax.set_ylabel('Lift Coefficient ($C_L$)', fontsize=11)
    ax.set_title('Phase Portrait: Drag vs Lift', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Force magnitude
    force_mag = np.sqrt(drag**2 + lift**2)
    ax = axes[1, 1]
    ax.plot(time, force_mag, 'purple', linewidth=2, label='Total Force')
    ax.set_xlabel('Time', fontsize=11)
    ax.set_ylabel('Force Magnitude', fontsize=11)
    ax.set_title('Total Force Magnitude vs Time', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved figure: {output_file}")
    return fig

def compute_strouhal(time, lift, re_number=1000):
    """Compute Strouhal number from lift oscillations"""

    # Skip initial transient (first 20% of data)
    transient_idx = int(0.2 * len(lift))
    time_steady = time[transient_idx:]
    lift_steady = lift[transient_idx:]

    if len(lift_steady) < 10:
        print("Not enough data for Strouhal computation")
        return None

    # Find peaks (local maxima) in lift signal
    peaks, properties = find_peaks(lift_steady, distance=5)

    if len(peaks) < 2:
        print("Not enough peaks detected for Strouhal computation")
        return None

    # Time between peaks
    peak_times = time_steady[peaks]
    periods = np.diff(peak_times)
    avg_period = np.mean(periods)
    frequency = 1.0 / avg_period

    # Strouhal number: St = f * D / U_inf
    # With D=1 (cylinder diameter), U_inf=1 (freestream)
    st = frequency

    return {
        'St': st,
        'frequency': frequency,
        'period': avg_period,
        'n_peaks': len(peaks),
        'lift_rms': np.std(lift_steady),
    }

def compute_statistics(time, drag, lift):
    """Compute statistics of forces"""
    # Skip first 20% as transient
    idx_start = int(0.2 * len(drag))

    drag_steady = drag[idx_start:]
    lift_steady = lift[idx_start:]

    stats = {
        'drag_mean': np.mean(drag_steady),
        'drag_std': np.std(drag_steady),
        'drag_min': np.min(drag_steady),
        'drag_max': np.max(drag_steady),
        'lift_mean': np.mean(lift_steady),
        'lift_std': np.std(lift_steady),
        'lift_min': np.min(lift_steady),
        'lift_max': np.max(lift_steady),
    }

    return stats

def plot_frequency_spectrum(time, lift, output_file='spectrum.png'):
    """Compute and plot frequency spectrum of lift"""

    # Skip transient
    transient_idx = int(0.2 * len(lift))
    lift_steady = lift[transient_idx:]
    time_steady = time[transient_idx:]

    # Compute sampling rate
    dt = np.mean(np.diff(time_steady))
    fs = 1.0 / dt

    # Welch's power spectral density estimate
    frequencies, Pxx = welch(lift_steady, fs=fs, nperseg=min(256, len(lift_steady)//2))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.semilogy(frequencies, Pxx, 'b-', linewidth=2)
    ax.set_xlabel('Frequency', fontsize=11)
    ax.set_ylabel('Power Spectral Density', fontsize=11)
    ax.set_title('Frequency Spectrum of Lift Coefficient', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, which='both')

    # Mark dominant frequency
    peak_idx = np.argmax(Pxx[1:]) + 1  # Skip DC component
    peak_freq = frequencies[peak_idx]
    ax.axvline(peak_freq, color='r', linestyle='--', linewidth=2, label=f'$f$ = {peak_freq:.4f}')
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved figure: {output_file}")
    return fig

def print_report(time, drag, lift, re_number=1000):
    """Print comprehensive analysis report"""

    stats = compute_statistics(time, drag, lift)
    strouhal_data = compute_strouhal(time, lift, re_number)

    print("\n" + "="*60)
    print("CYLINDER FLOW SIMULATION - ANALYSIS REPORT")
    print("="*60)
    print(f"\nSimulation Parameters:")
    print(f"  Reynolds Number: {re_number}")
    print(f"  Simulation time: {time[0]:.2f} to {time[-1]:.2f}")
    print(f"  Number of time steps: {len(time)}")
    print(f"  Time step size: {np.mean(np.diff(time)):.6f}")

    print(f"\nForce Coefficients (Steady-state statistics):")
    print(f"  Drag Coefficient:")
    print(f"    Mean:   {stats['drag_mean']:.6f}")
    print(f"    Std:    {stats['drag_std']:.6f}")
    print(f"    Min:    {stats['drag_min']:.6f}")
    print(f"    Max:    {stats['drag_max']:.6f}")

    print(f"  Lift Coefficient:")
    print(f"    Mean:   {stats['lift_mean']:.6f}")
    print(f"    Std:    {stats['lift_std']:.6f}")
    print(f"    Min:    {stats['lift_min']:.6f}")
    print(f"    Max:    {stats['lift_max']:.6f}")

    if strouhal_data:
        print(f"\nVortex Shedding Analysis:")
        print(f"  Strouhal Number: {strouhal_data['St']:.6f}")
        print(f"  Oscillation Frequency: {strouhal_data['frequency']:.6f}")
        print(f"  Period: {strouhal_data['period']:.6f}")
        print(f"  Number of peaks detected: {strouhal_data['n_peaks']}")
        print(f"  Lift RMS: {strouhal_data['lift_rms']:.6f}")

        # Reference values for Re=1000
        ref_st = 0.215  # typical experimental value
        print(f"\nReference (Experimental) Strouhal Number at Re=1000: {ref_st:.3f}")
        if strouhal_data['St'] > 0:
            error = abs(strouhal_data['St'] - ref_st) / ref_st * 100
            print(f"Relative error: {error:.1f}%")

    print("\n" + "="*60)

def main():
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend

    # Find forces file
    if len(sys.argv) > 1:
        forces_file = sys.argv[1]
    else:
        forces_file = 'forces.dat'

    if not os.path.exists(forces_file):
        print(f"Error: {forces_file} not found")
        print("Usage: python plot_forces.py [forces_file]")
        sys.exit(1)

    # Load data
    time, drag, lift = load_forces(forces_file)
    if time is None:
        sys.exit(1)

    # Generate plots
    plot_forces(time, drag, lift, 'forces_history.png')
    plot_frequency_spectrum(time, lift, 'spectrum.png')

    # Print report
    print_report(time, drag, lift)

    print("\nGenerated files:")
    print("  - forces_history.png")
    print("  - spectrum.png")

if __name__ == '__main__':
    main()
