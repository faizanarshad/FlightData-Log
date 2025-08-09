# Flight Data Analysis - User Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/Flight_data_log.git
cd Flight_data_log

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Running the Analysis
```bash
# Run all analysis (recommended for first time)
python main.py all

# Or run individual components
python main.py analyze      # Data analysis only
python main.py visualize    # Generate visualizations
python main.py dashboard    # Create dashboards
```

### Viewing Results
After running the analysis, you can view the results:
- **Main Dashboard**: Open `src/dashboard/beautiful_dashboard.html` in your browser
- **All Dashboards**: Check the `src/dashboard/` directory for all HTML files
- **Images**: Check `static/images/` for static visualizations

## Installation

### Option 1: Standard Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Option 2: Development Installation
```bash
# Install with development dependencies
make install-dev

# Or manually
pip install -r requirements.txt
pip install -e ".[dev,docs]"
```

### Option 3: Using Makefile
```bash
# Complete setup including development tools
make setup
```

## Usage

### Command Line Interface

The project provides a comprehensive CLI through `main.py`:

```bash
# Get help
python main.py --help

# Run specific analysis
python main.py analyze --output reports/
python main.py visualize --data custom_data.csv
python main.py dashboard --output dashboards/

# Run everything with custom settings
python main.py all --output results/ --data data/raw/my_data.csv
```

### Using Makefile Commands

```bash
# Quick start (setup + run all)
make quick-start

# Individual commands
make run-analysis
make run-viz
make run-dashboard
make all

# Development commands
make test
make lint
make format
make clean
```

### Python API

You can also use the project as a Python library:

```python
from src.analysis.read_dataset import load_data
from src.visualization.advanced_visualizations import create_visualizations
from src.dashboard.beautiful_dashboard import create_dashboard

# Load data
df = load_data('data/raw/airlines_flights_data.csv')

# Create visualizations
create_visualizations(df)

# Create dashboard
create_dashboard(df)
```

## Project Structure

```
Flight_data_log/
├── main.py                    # Main entry point
├── setup.py                   # Package setup
├── requirements.txt           # Dependencies
├── Makefile                   # Build automation
├── .gitignore                # Git ignore rules
├── README.md                 # Project overview
│
├── src/                      # Source code
│   ├── __init__.py
│   ├── analysis/             # Data analysis modules
│   │   ├── __init__.py
│   │   ├── read_dataset.py
│   │   └── data_analysis_explorer.py
│   ├── visualization/        # Visualization modules
│   │   ├── __init__.py
│   │   └── advanced_visualizations.py
│   └── dashboard/            # Dashboard modules
│       ├── __init__.py
│       ├── modern_dashboard.py
│       ├── beautiful_dashboard.py
│       └── *.html           # Generated dashboards
│
├── data/                     # Data files
│   ├── raw/                  # Original data
│   │   └── airlines_flights_data.csv
│   └── processed/            # Processed data
│       └── dataset_summary.txt
│
├── config/                   # Configuration files
│   └── config.yaml          # Main configuration
│
├── static/                   # Static assets
│   └── images/              # Generated images
│       ├── airline_wordcloud.png
│       └── price_analysis.png
│
├── docs/                     # Documentation
│   ├── api/                 # API documentation
│   └── user_guide/          # User guides
│
├── tests/                    # Test files
├── notebooks/                # Jupyter notebooks
├── output/                   # Generated output (gitignored)
├── logs/                     # Log files (gitignored)
└── reports/                  # Analysis reports (gitignored)
```

## Configuration

### Main Configuration File

The project uses `config/config.yaml` for centralized configuration:

```yaml
# Data Configuration
data:
  raw_data_path: "data/raw/airlines_flights_data.csv"
  processed_data_path: "data/processed/"
  output_path: "output/"

# Analysis Configuration
analysis:
  sample_size: null  # null for full dataset
  random_state: 42
  correlation_threshold: 0.5
  outlier_threshold: 3.0

# Visualization Configuration
visualization:
  theme: "plotly_white"
  color_palette: "viridis"
  figure_width: 1200
  figure_height: 800
```

### Environment Variables

You can override configuration using environment variables:

```bash
export FLIGHT_DATA_PATH="path/to/your/data.csv"
export FLIGHT_OUTPUT_DIR="custom/output/path"
```

### Custom Configuration

Create a local configuration file for custom settings:

```bash
cp config/config.yaml config/local_config.yaml
# Edit local_config.yaml with your settings
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install in development mode
pip install -e .
```

#### 2. Missing Dependencies
```bash
# Solution: Install all requirements
pip install -r requirements.txt
```

#### 3. Memory Issues with Large Datasets
```bash
# Solution: Use sampling in config
# Edit config/config.yaml:
analysis:
  sample_size: 10000  # Limit to 10k records
```

#### 4. Dashboard Not Loading
```bash
# Solution: Check file paths and permissions
ls -la src/dashboard/
# Ensure HTML files are generated
```

#### 5. Visualization Errors
```bash
# Solution: Check matplotlib backend
export MPLBACKEND=Agg  # For headless environments
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization

For large datasets:

1. **Use sampling**:
   ```yaml
   analysis:
     sample_size: 50000
   ```

2. **Enable multiprocessing**:
   ```yaml
   performance:
     use_multiprocessing: true
     max_workers: 4
   ```

3. **Use chunked processing**:
   ```yaml
   performance:
     chunk_size: 5000
   ```

## FAQ

### Q: How do I add my own data?
A: Place your CSV file in `data/raw/` and update the path in `config/config.yaml` or use the `--data` parameter.

### Q: Can I customize the visualizations?
A: Yes! Edit the configuration in `config/config.yaml` or modify the visualization functions in `src/visualization/`.

### Q: How do I create a custom dashboard?
A: Create a new Python file in `src/dashboard/` following the pattern of existing files.

### Q: Can I run this on a server without display?
A: Yes! Use `export MPLBACKEND=Agg` and the dashboards will be generated as HTML files.

### Q: How do I contribute to the project?
A: See the main README.md for contribution guidelines.

### Q: What if I encounter memory issues?
A: Use sampling by setting `sample_size` in the configuration or process data in chunks.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Flight_data_log/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Flight_data_log/discussions)
- **Documentation**: Check the `docs/` directory for more detailed guides

---

For more information, see the main [README.md](../README.md) file. 