import pandas as pd
from modules.data_audit import run_audit
from modules.loaders import load_data

def test():
    file_path = "1_crash_reports.csv"
    print(f"Loading {file_path}...")
    df = load_data(file_path)
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
