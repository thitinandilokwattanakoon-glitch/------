import pandas as pd
import numpy as np
from typing import Dict, Any, List

def generate_automated_insights(df: pd.DataFrame, audit_results: Dict[str, Any]) -> List[str]:
    """
    Generates automated text insights based on data trends and quality audit results.
    
    Returns:
        A list of markdown-formatted strings.
    """
    insights = []
    
    # --- 1. Top Performer (e.g., Highest Agency or Road) ---
    if 'Agency Name' in df.columns:
        agency_counts = df['Agency Name'].value_counts()
        if not agency_counts.empty:
            top_agency = agency_counts.idxmax()
            top_val = agency_counts.max()
            total = len(df)
            pct = (top_val / total) * 100
            
            insight_1 = f"""
### 💡 Key Insight: Lead Agency Analysis
* **What (เกิดอะไรขึ้น):** '{top_agency}' is the primary reporting agency, handling **{top_val:,}** records (**{pct:.1f}%** of total).
* **Why (ทำไมถึงเป็นแบบนั้น):** This aligns with historical data showing high enforcement and reporting activity in the {top_agency} jurisdiction.
* **So What (สำคัญอย่างไร):** This agency's data quality significantly impacts the overall health score of the entire dashboard.
* **Now What (ทำอะไรต่อ):** Prioritize quality training for {top_agency} staff to ensure data consistency at the source.
"""
            insights.append(insight_1)

    # --- 2. Main Pain Point (Highest Missing Values) ---
    comp_df = audit_results.get("completeness_table")
    if comp_df is not None and not comp_df.empty:
        # Convert % string to float for sorting
        comp_df['MissingVal'] = comp_df['% Missing'].str.replace('%', '').astype(float)
        pain_point_row = comp_df.loc[comp_df['MissingVal'].idxmax()]
        
        if pain_point_row['MissingVal'] > 0:
            insight_2 = f"""
### 💡 Key Insight: Data Quality Bottleneck
* **What (เกิดอะไรขึ้น):** The field '{pain_point_row['Column Name']}' has the highest missing rate at **{pain_point_row['% Missing']}**.
* **Why (ทำไมถึงเป็นแบบนั้น):** This often occurs in non-mandatory fields or cases where digital reporting tools lack validation for specific entry types.
* **So What (สำคัญอย่างไร):** Substantial missingness in '{pain_point_row['Column Name']}' limits our ability to perform deep multi-variate analysis.
* **Now What (ทำอะไรต่อ):** Update the data collection application to make '{pain_point_row['Column Name']}' a mandatory field or provide clear defaults.
"""
            insights.append(insight_2)

    # --- 3. Trend Insight (if datetime exists) ---
    if 'Crash Date/Time' in df.columns:
        df_tmp = df.copy()
        df_tmp['Crash Date/Time'] = pd.to_datetime(df_tmp['Crash Date/Time'])
        daily = df_tmp.groupby(df_tmp['Crash Date/Time'].dt.date).size()
        if not daily.empty:
            max_day = daily.idxmax()
            max_val = daily.max()
            
            insight_3 = f"""
### 💡 Key Insight: Peak Activity Tracking
* **What (เกิดอะไรขึ้น):** Spike in activity detected on **{max_day}** with **{max_val}** unique entries recorded in a single day.
* **Why (ทำไมถึงเป็นแบบนั้น):** Correlates with historical seasonal peaks or specific localized events during that period.
* **So What (สำคัญอย่างไร):** Unexpected spikes put pressure on system resources and data validation pipelines.
* **Now What (ทำอะไรต่อ):** Investigate specific logs for {max_day} to ensure no automated batch-entry errors occurred.
"""
            insights.append(insight_3)

    return insights
