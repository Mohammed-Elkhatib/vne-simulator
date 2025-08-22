import matplotlib.pyplot as plt
import os
from ..metrics.metrics import calculate_acceptance_ratio


def _calculate_cumulative_acceptance(successes):
    """Calculate cumulative acceptance ratio over time."""
    cumulative_success = []
    total_so_far = 0
    success_so_far = 0
    
    for success in successes:
        total_so_far += 1
        success_so_far += success
        cumulative_success.append(success_so_far / total_so_far)
    
    return cumulative_success


def _extract_timeline_data(results):
    """Extract arrival times and success data from results."""
    arrival_times = [r['arrival_time'] for r in results]
    successes = [1 if r['success'] else 0 for r in results]
    return arrival_times, successes


def _add_summary_stats(results, position='bottom_left'):
    """Add summary statistics box to current plot."""
    total = len(results)
    successful = sum(1 if r['success'] else 0 for r in results)
    acceptance_ratio = calculate_acceptance_ratio(results)
    
    if position == 'bottom_left':
        plt.text(1.05, 0.5, f'Total VNRs: {total}\nSuccessful: {successful}\nAcceptance Ratio: {acceptance_ratio:.3f}',
                 transform=plt.gca().transAxes, verticalalignment='center', horizontalalignment='left',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    elif position == 'top_left':
        plt.text(0.02, 0.98, f'Total VNRs: {total}\nSuccessful: {successful}\nAcceptance Ratio: {acceptance_ratio:.3f}',
                 transform=plt.gca().transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    elif position == 'bottom_right':
        plt.text(0.98, 0.02, f'Total VNRs: {total}\nSuccessful: {successful}\nAcceptance Ratio: {acceptance_ratio:.3f}',
                 transform=plt.gca().transAxes, verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    elif position == 'outside_right':
        # Use axes coordinates like the legend positioning in algorithm comparison
        plt.text(1.05, 0.5, f'Total VNRs: {total}\nSuccessful: {successful}\nAcceptance Ratio: {acceptance_ratio:.3f}',
                 transform=plt.gca().transAxes, verticalalignment='center', horizontalalignment='left',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))


def _save_plot(filename, folder="pictures"):
    """Save plot with consistent settings."""
    filepath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')


def plot_simulation_timeline(results, title="Simulation Timeline", figsize=(12, 10), filename=None):
    """Plot timeline showing success/failure pattern and cumulative acceptance ratio."""
    arrival_times, successes = _extract_timeline_data(results)
    
    # Create timeline visualization with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    
    # Plot 1: Success/failure scatter
    colors = ['green' if s else 'red' for s in successes]
    ax1.scatter(arrival_times, successes, c=colors, alpha=0.7, s=100)
    ax1.set_ylabel('Success (1) / Failure (0)')
    ax1.set_title(f'{title} - Success/Failure Pattern')
    ax1.set_ylim(-0.1, 1.1)  # Ensure proper Y-axis range
    ax1.set_yticks([0, 1])   # Only show 0 and 1 on Y-axis
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cumulative acceptance ratio over time
    cumulative_success = _calculate_cumulative_acceptance(successes)
    ax2.plot(arrival_times, cumulative_success, 'b-', linewidth=2, marker='o')
    ax2.set_xlabel('Arrival Time')
    ax2.set_ylabel('Cumulative Acceptance Ratio')
    ax2.set_title('Cumulative Performance Over Time')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)
    
    plt.tight_layout()
    
    # Make space for the statistics box on the right
    plt.subplots_adjust(right=0.75)
    
    # Add summary stats outside the plot area to avoid any overlap
    _add_summary_stats(results, 'outside_right')
    
    if filename is None:
        filename = title.replace(" ", "_").lower() + ".png"
    _save_plot(filename)
    plt.show()


def plot_algorithm_comparison(results_dict, figsize=(15, 6), filename="algorithm_comparison.png", colors=None):
    """Plot algorithm comparison with acceptance ratios and cumulative performance."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot 1: Acceptance ratios
    algorithms = list(results_dict.keys())
    acceptance_ratios = [calculate_acceptance_ratio(results) for results in results_dict.values()]
    
    if colors is None:
        colors = ['blue', 'green', 'red', 'orange'][:len(algorithms)]
    
    bars = ax1.bar(algorithms, acceptance_ratios, color=colors)
    ax1.set_ylabel('Acceptance Ratio')
    ax1.set_title('Algorithm Acceptance Ratios')
    ax1.set_ylim(0, 1.05)
    
    # Add value labels on bars with overlap handling
    for i, (bar, ratio) in enumerate(zip(bars, acceptance_ratios)):
        height = bar.get_height()
        # Offset label if same value as previous to avoid overlap
        offset = 0.01
        if i > 0 and abs(acceptance_ratios[i] - acceptance_ratios[i-1]) < 0.001:
            offset = 0.03  # Higher offset for identical values
        ax1.text(bar.get_x() + bar.get_width()/2., height + offset,
                f'{ratio:.3f}', ha='center', va='bottom')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Cumulative performance over time
    for alg_name, results in results_dict.items():
        arrival_times, successes = _extract_timeline_data(results)
        cumulative_success = _calculate_cumulative_acceptance(successes)
        ax2.plot(arrival_times, cumulative_success, marker='o', label=alg_name, linewidth=2)
    
    ax2.set_xlabel('Arrival Time')
    ax2.set_ylabel('Cumulative Acceptance Ratio')
    ax2.set_title('Cumulative Acceptance Ratio Over Time')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)
    
    plt.tight_layout()
    _save_plot(filename)
    plt.show()


def plot_simulation_results(results, title="Simulation Results", figsize=(12, 6), filename=None):
    """Plot simple simulation results showing success/failure pattern."""
    arrival_times, successes = _extract_timeline_data(results)
    
    plt.figure(figsize=figsize)
    
    # Plot success/failure
    colors = ['green' if s else 'red' for s in successes]
    plt.scatter(arrival_times, successes, c=colors, alpha=0.7, s=100)
    
    plt.xlabel('Arrival Time')
    plt.ylabel('Success (1) / Failure (0)')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    
    # Make space for the statistics box on the right
    plt.subplots_adjust(right=0.75)
    
    _add_summary_stats(results, 'outside_right')
    
    if filename is None:
        filename = title.replace(" ", "_").lower() + ".png"
    _save_plot(filename)
    plt.show()