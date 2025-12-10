import pandas as pd
import seaborn as sns
import matplotlib
# Force backend to Agg before importing pyplot
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

# --- Configuration ---
DATA_FILE = 'data/banxico_rates.csv'
PLOT_DIR = 'plots'
PLOT_FILE = f'{PLOT_DIR}/data_availability.png'

os.makedirs(PLOT_DIR, exist_ok=True)

print("Generating visualization...")

# FAIL FAST: Check if data exists
if not os.path.exists(DATA_FILE):
    print(f"CRITICAL ERROR: {DATA_FILE} not found.")
    sys.exit(1)

try:
    # 1. Read the data
    df = pd.read_csv(DATA_FILE, index_col='Date', parse_dates=True)

    if df.empty:
        print("Data loaded but DataFrame is empty.")
        sys.exit(1)

    # 2. Prepare Data for Heatmap
    # .notna() -> converts real values to True, NaNs to False
    # .astype(int) -> converts True/False to 1/0 (Fixes the .any() crash)
    # .resample('QE') -> Resamples to Quarter End (Fixes the deprecation warning)
    # .max() -> If any 1 exists in the quarter, the max is 1 (True). If all are 0, max is 0 (False).
    presence_df = df.notna().astype(int).resample('QE').max().T

    # --- Plotting ---
    plt.figure(figsize=(15, 10))

    # cmap: 0 (False) = light red, 1 (True) = green
    ax = sns.heatmap(presence_df, cmap=["#ffebeb", "#28a745"], cbar=False, 
                     linewidths=0.5, linecolor='white', square=False)

    plt.title('Timeline of Mexican Government Securities Availability', fontsize=16, pad=20)
    plt.ylabel('Instrument', fontsize=12)
    plt.xlabel('Year', fontsize=12)

    # Clean X-axis labels to show Year only
    # We iterate through the existing labels to format them
    new_labels = []
    for item in ax.get_xticklabels():
        try:
            # Try to parse the label text as a year (e.g., "2023-03-31" -> "2023")
            text = item.get_text()
            # Depending on pandas version, text might be full date or just year
            new_labels.append(text[:4]) 
        except:
            new_labels.append(item.get_text())
            
    ax.set_xticklabels(new_labels, rotation=45, ha='right')
    
    # Reduce clutter: Only show every 4th tick (One label per year if data is quarterly)
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if i % 4 != 0:
            label.set_visible(False)

    plt.tight_layout()

    plt.savefig(PLOT_FILE, dpi=150, bbox_inches='tight')
    print(f"Success: Plot saved to {PLOT_FILE}")

except Exception as e:
    print(f"An error occurred during plotting: {e}")
    # Print the full traceback for easier debugging if it happens again
    import traceback
    traceback.print_exc()
    sys.exit(1)
