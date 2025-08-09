# Jupyter Notebooks

This directory contains Jupyter notebooks for interactive data analysis and exploration.

## Available Notebooks

### 01_data_exploration.ipynb
- **Purpose**: Initial data exploration and understanding
- **Content**: 
  - Data loading and overview
  - Data quality checks
  - Basic statistical analysis
  - Interactive visualizations
  - Key insights summary

## How to Use

1. **Start Jupyter Lab**:
   ```bash
   jupyter lab
   ```

2. **Navigate to notebooks directory**:
   ```bash
   cd notebooks/
   ```

3. **Open the notebook**:
   - Click on `01_data_exploration.ipynb`
   - Or run: `jupyter notebook 01_data_exploration.ipynb`

## Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install jupyter lab notebook
pip install -r ../requirements.txt
```

## Tips

- Run cells in order from top to bottom
- Check the output of each cell before proceeding
- Save your work frequently
- Export results to HTML or PDF for sharing

## Creating New Notebooks

When creating new notebooks:

1. Use descriptive names (e.g., `02_price_analysis.ipynb`)
2. Include markdown cells for documentation
3. Add clear section headers
4. Include code comments
5. Save outputs and visualizations

## Example Notebook Structure

```python
# 1. Setup and Imports
import pandas as pd
import numpy as np
# ... other imports

# 2. Data Loading
df = pd.read_csv('../data/raw/airlines_flights_data.csv')

# 3. Data Exploration
print(df.info())
print(df.describe())

# 4. Analysis
# ... your analysis code

# 5. Visualizations
# ... your visualization code

# 6. Conclusions
# ... summary and insights
``` 