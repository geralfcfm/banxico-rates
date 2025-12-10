import pandas as pd
import seaborn as sns
import matplotlib
# Use 'Agg' backend to prevent "no display name" errors on GitHub Actions
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
import sys

# --- Configuration ---
DATA_FILE = 'data/banxico_rates.csv'
PLOT_DIR = 'plots'
PLOT_FILE = f'{PLOT_DIR}/data_availability.png'

# Ensure plots directory exists
os.makedirs(PLOT_DIR, exist_ok=True)

print("Generating visualization...")

# Check if data exists BEFORE trying to read it
if not os.path.exists(DATA_FILE):
    print(f"CRITICAL ERROR: {DATA_FILE} not found.")
    print("Did the data pipeline run and COMMIT the csv to the repo?")
    sys.exit(1) # Fail the workflow immediately

try:
    # 1. Read the data
    df = pd.read_csv(DATA_FILE, index_col='Date', parse_dates=True)

    if df.empty:
        print("Data loaded but DataFrame is empty.")
        sys.exit(1)

    # 2. Create boolean mask
    presence_df = df.notna().resample('Q').any().T 

    # --- Plotting ---
    plt.figure(figsize=(15, 10))

    ax = sns.heatmap(presence_df, cmap=["#ffebeb", "#28a745"], cbar=False, 
                     linewidths=0.5, linecolor='white', square=False)

    plt.title('Timeline of Mexican Government Securities Availability', fontsize=16, pad=20)
    plt.ylabel('Instrument', fontsize=12)
    plt.xlabel('Year', fontsize=12)

    # Clean X-axis labels
    labels = [item.get_text()[:4] for item in ax.get_xticklabels()]
    ax.set_xticklabels(labels, rotation=45, ha='right')
    
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if i % 4 != 0:
            label.set_visible(False)

    plt.tight_layout()

    # 3. Save the image
    plt.savefig(PLOT_FILE, dpi=150, bbox_inches='tight')
    print(f"Success: Plot saved to {PLOT_FILE}")

except Exception as e:
    print(f"An error occurred during plotting: {e}")
    sys.exit(1) # Ensure the Action fails if plotting crashes
