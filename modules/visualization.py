import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional

def plot_trend(df: pd.DataFrame, date_col: str, value_col: Optional[str] = None, rolling_window: int = 0):
    """
    Plots a time-series trend chart.
    """
    df_plot = df.copy()
    df_plot[date_col] = pd.to_datetime(df_plot[date_col])
    
    # Aggregating by date (count or sum)
    if value_col:
        daily_data = df_plot.groupby(df_plot[date_col].dt.date)[value_col].sum().reset_index()
    else:
        daily_data = df_plot.groupby(df_plot[date_col].dt.date).size().reset_index(name='Count')
        value_col = 'Count'
    
    daily_data.columns = ['Date', value_col]
    daily_data = daily_data.sort_values('Date')
    
    fig = px.line(daily_data, x='Date', y=value_col, title=f"Trend Analysis: {value_col} over Time",
                  template="plotly_white", color_discrete_sequence=['#1E88E5'])
    
    if rolling_window > 0:
        daily_data['Rolling Mean'] = daily_data[value_col].rolling(window=rolling_window).mean()
        fig.add_scatter(x=daily_data['Date'], y=daily_data['Rolling Mean'], 
                        name=f'{rolling_window}-Day Rolling Mean', line=dict(color='#C62828', width=2))
        
    fig.update_layout(xaxis_title="Date", yaxis_title=value_col, hovermode="x unified")
    return fig

def plot_distribution(df: pd.DataFrame, num_col: str, show_outliers: bool = True, plot_type: str = "Histogram"):
    """
    Plots a distribution chart with optional outlier visibility.
    """
    if plot_type == "Histogram":
        fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}",
                           template="plotly_white", color_discrete_sequence=['#1E88E5'],
                           marginal="box" if show_outliers else None)
    else:
        fig = px.box(df, y=num_col, title=f"Boxplot of {num_col}",
                     points="all" if show_outliers else "outliers", # Plotly box points: outliers only shows outliers, False none, "all" points
                     template="plotly_white", color_discrete_sequence=['#1E88E5'])
    
    fig.update_layout(xaxis_title=num_col, bargap=0.1)
    return fig

def plot_comparison(df: pd.DataFrame, cat_col: str, top_n: int = 10):
    """
    Plots a categorical comparison bar chart.
    """
    counts = df[cat_col].value_counts().reset_index()
    counts.columns = [cat_col, 'Count']
    counts = counts.sort_values('Count', ascending=False).head(top_n)
    
    fig = px.bar(counts, x=cat_col, y='Count', title=f"Top {top_n} {cat_col}",
                 template="plotly_white", color='Count', color_continuous_scale='Blues')
    
    fig.update_layout(xaxis_title=cat_col, yaxis_title="Number of Records", 
                      xaxis={'categoryorder':'total descending'})
    return fig

def plot_heatmap(df: pd.DataFrame):
    """
    Plots a correlation heatmap for numerical features.
    """
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty or len(num_df.columns) < 2:
        return None
        
    corr = num_df.corr()
    
    fig = px.imshow(corr, text_auto=True, aspect="auto", 
                    color_continuous_scale='RdBu_r', 
                    title="Correlation Matrix (Numerical Features)",
                    template="plotly_white")
    return fig

def plot_scatter(df: pd.DataFrame, x_col: str, y_col: str):
    """
    Plots a scatter plot with sampling for high performance.
    """
    is_sampled = False
    n_rows = len(df)
    
    if n_rows > 50000:
        df_plot = df.sample(n=10000, random_state=42)
        is_sampled = True
    else:
        df_plot = df
        
    title = f"Correlation: {x_col} vs {y_col}"
    if is_sampled:
        title += " (Sampled 10k Records for Performance)"
        
    fig = px.scatter(df_plot, x=x_col, y=y_col, title=title,
                     template="plotly_white", opacity=0.5, color_discrete_sequence=['#1E88E5'])
    
    fig.update_layout(hovermode="closest")
    return fig
