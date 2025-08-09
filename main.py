#!/usr/bin/env python3
"""
Flight Data Analysis - Main Entry Point
=======================================

This is the main entry point for the Flight Data Analysis project.
It provides easy access to all analysis, visualization, and dashboard functionality.

Usage:
    python main.py --help
    python main.py analyze
    python main.py visualize
    python main.py dashboard
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    parser = argparse.ArgumentParser(
        description="Flight Data Analysis - Comprehensive airline data analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py analyze                    # Run data analysis
  python main.py visualize                  # Generate visualizations
  python main.py dashboard                  # Create interactive dashboards
  python main.py analyze --output reports/  # Save analysis to reports directory
        """
    )
    
    parser.add_argument(
        'command',
        choices=['analyze', 'visualize', 'dashboard', 'all'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--output',
        default='output/',
        help='Output directory for generated files (default: output/)'
    )
    
    parser.add_argument(
        '--data',
        default='data/raw/airlines_flights_data.csv',
        help='Path to the dataset (default: data/raw/airlines_flights_data.csv)'
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    if args.command == 'analyze':
        run_analysis(args)
    elif args.command == 'visualize':
        run_visualization(args)
    elif args.command == 'dashboard':
        run_dashboard(args)
    elif args.command == 'all':
        run_analysis(args)
        run_visualization(args)
        run_dashboard(args)

def run_analysis(args):
    """Run data analysis scripts."""
    print("🔍 Running data analysis...")
    try:
        from src.analysis.read_dataset import main as read_main
        from src.analysis.data_analysis_explorer import main as explorer_main
        
        print("  - Reading dataset...")
        read_main()
        
        print("  - Running comprehensive analysis...")
        explorer_main()
        
        print("✅ Analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

def run_visualization(args):
    """Run visualization scripts."""
    print("📊 Generating visualizations...")
    try:
        from src.visualization.advanced_visualizations import main as viz_main
        
        viz_main()
        print("✅ Visualizations generated successfully!")
        
    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        sys.exit(1)

def run_dashboard(args):
    """Run dashboard generation scripts."""
    print("🎨 Creating interactive dashboards...")
    try:
        from src.dashboard.modern_dashboard import main as modern_main
        from src.dashboard.beautiful_dashboard import main as beautiful_main
        
        print("  - Creating modern dashboard...")
        modern_main()
        
        print("  - Creating beautiful dashboard...")
        beautiful_main()
        
        print("✅ Dashboards created successfully!")
        print(f"📁 Dashboards saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Error during dashboard creation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 