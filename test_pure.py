import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add current dir to sys.path
sys.path.append(os.getcwd())

from modules.data_audit import run_audit

def load_data_pure(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    return df

def test():
    file_path = "1_crash_reports.csv"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print(f"Loading {file_path}...")
    df = load_data_pure(file_path)
    print(f"Loaded {len(df)} rows.")
    
    print("Running Audit...")
    results = run_audit(df)
    
    print(f"\nHealth Score: {results['health_score']}/100")
    print("\nSummary:")
    for msg in results['summary']:
        print(f"- {msg}")
        
    print("\nCompleteness Table (first 5):")
    print(results['completeness_table'].head())

if __name__ == "__main__":
    test()
