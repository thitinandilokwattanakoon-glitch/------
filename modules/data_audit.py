import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple

def detect_outliers_iqr(df: pd.DataFrame, column: str) -> Tuple[int, pd.Series]:
    """Detects outliers using the Interquartile Range (IQR) method."""
    if not np.issubdtype(df[column].dtype, np.number):
        return 0, pd.Series([False] * len(df))
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    return outliers.sum(), outliers

def run_audit(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs a 4-dimensional Data Quality Audit (Completeness, Consistency, Accuracy, Timeliness).

    Returns:
        A dictionary containing audit results, metrics, and a summary.
    """
    audit_results = {
        "completeness": {},
        "consistency": {},
        "accuracy": {},
        "timeliness": {},
        "outliers": {},
        "summary": [],
        "reconciliation": {
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Memory Usage (MB)": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}"
        },
        "health_score": 100
    }

    n_rows = len(df)
    if n_rows == 0:
        return {"health_score": 0, "summary": ["Dataset is empty."], "column_stats": pd.DataFrame()}

    # 1. COMPLETENESS & PROFILE
    missing_stats = df.isnull().mean() * 100
    key_fields = ['Report Number', 'Crash Date/Time', 'Vehicle ID', 'Person ID']
    col_audit_data = []
    
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in df.columns:
        missing_pct = missing_stats[col]
        unique_vals = df[col].nunique()
        dtype = str(df[col].dtype)
        
        # Outlier Detection for numerical columns
        outlier_count = 0
        if col in num_cols:
            outlier_count, _ = detect_outliers_iqr(df, col)
            if outlier_count > 0:
                audit_results["outliers"][col] = outlier_count
        
        status = "Valid"
        if missing_pct > 10:
            status = "Critical"
            if col in key_fields:
                audit_results["summary"].append(f"🔴 Critical: Key field '{col}' has {missing_pct:.2f}% missing values.")
                audit_results["health_score"] -= 10
        elif missing_pct > 1:
            status = "Warning"
            if col in key_fields:
                audit_results["summary"].append(f"🟠 Warning: Key field '{col}' has {missing_pct:.2f}% missing values.")
                audit_results["health_score"] -= 5
        elif missing_pct > 0:
            status = "Warning"
            
        col_audit_data.append({
            "Column Name": col,
            "Type": dtype,
            "% Missing": f"{missing_pct:.2f}%",
            "Unique Values": unique_vals,
            "Outliers (IQR)": outlier_count,
            "Status": status
        })

    audit_results["completeness_table"] = pd.DataFrame(col_audit_data)

    # 2. CONSISTENCY CHECK
    pk_col = 'Report Number'
    if pk_col in df.columns:
        duplicate_count = df.duplicated(subset=[pk_col]).sum()
        duplicate_rate = (duplicate_count / n_rows) * 100
        audit_results["consistency"] = {
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_rate
        }
        if duplicate_count > 0:
            audit_results["summary"].append(f"⚠️ Found {duplicate_count} duplicate '{pk_col}' entries ({duplicate_rate:.2f}% rate).")
            audit_results["health_score"] -= min(20, int(duplicate_rate * 2))
    
    # 3. ACCURACY CHECK
    accuracy_issues = []
    if 'Crash Date/Time' in df.columns:
        try:
            tmp_dates = pd.to_datetime(df['Crash Date/Time'], errors='coerce')
            future_dates = (tmp_dates > datetime.now()).sum()
            if future_dates > 0:
                accuracy_issues.append(f"❌ Found {future_dates} records with crash dates in the future.")
                audit_results["health_score"] -= 10
        except Exception:
            pass

    if 'Vehicle Year' in df.columns:
        try:
            current_year = datetime.now().year
            vehicle_years = pd.to_numeric(df['Vehicle Year'], errors='coerce')
            future_vehicles = (vehicle_years > current_year + 1).sum()
            if future_vehicles > 0:
                accuracy_issues.append(f"🚗 Found {future_vehicles} vehicles with invalid future model years.")
                audit_results["health_score"] -= 5
        except Exception:
            pass

    audit_results["summary"].extend(accuracy_issues)

    # 4. TIMELINESS CHECK
    if 'Crash Date/Time' in df.columns:
        try:
            tmp_dates = pd.to_datetime(df['Crash Date/Time'], errors='coerce').dropna()
            if not tmp_dates.empty:
                latest_date = tmp_dates.max()
                delta_days = (datetime.now() - latest_date).days
                audit_results["timeliness"] = {"latest": latest_date, "delta": delta_days}
                status_emoji = "✅" if delta_days < 180 else "⏳"
                audit_results["summary"].append(f"{status_emoji} Timeliness: Latest record is from {latest_date.strftime('%Y-%m-%d')} ({delta_days} days old).")
        except Exception:
            pass

    audit_results["health_score"] = max(0, min(100, audit_results["health_score"]))
    return audit_results
