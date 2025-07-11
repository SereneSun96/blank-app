import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
import altair as alt

st.title("Data App Assignment, by Yanran Sun, on March 29th 2025")

st.write("### Display data")
df = pd.read_csv("Superstore_Sales_utf8.csv", parse_dates=True)
st.dataframe(df)

# This bar chart will not have solid bars--but lines--because the detail data is being graphed independently
st.bar_chart(df, x="Category", y="Sales")

# Now let's do the same graph where we do the aggregation first in Pandas... (this results in a chart with solid bars)
st.dataframe(df.groupby("Category").sum())
# Using as_index=False here preserves the Category as a column.  If we exclude that, Category would become the datafram index and we would need to use x=None to tell bar_chart to use the index
st.bar_chart(df.groupby("Category", as_index=False).sum(), x="Category", y="Sales", color="#04f")

# Aggregating by time
# Here we ensure Order_Date is in datetime format, then set is as an index to our dataframe
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df.set_index('Order_Date', inplace=True)
# Here the Grouper is using our newly set index to group by Month ('M')
sales_by_month = df.filter(items=['Sales']).groupby(pd.Grouper(freq='M')).sum()

st.dataframe(sales_by_month)

# Here the grouped months are the index and automatically used for the x axis
st.line_chart(sales_by_month, y="Sales")

import streamlit as st
import pandas as pd

# Load data
@st.cache_data  # Cache data to improve performance
def load_data():
    df = pd.read_csv("Superstore_Sales_utf8.csv")  # Ensure the file contains 'Category', 'Sub_Category', 'Sales', 'Profit' columns
    return df

df = load_data()

# Title
st.title("Sales Data Analysis App")

st.write("### (1) add a drop down for Category")
# (1) Add a dropdown to select Category
category = st.selectbox("Select Category", df["Category"].unique())

st.write("### (2) add a multi-select for Sub_Category *in the selected Category (1)*")
# (2) Add a multi-select to choose Sub_Category
sub_categories = st.multiselect(
    "Select Sub_Category",
    df[df["Category"] == category]["Sub_Category"].unique()
)

# Filter data
filtered_data = df[(df["Category"] == category) & (df["Sub_Category"].isin(sub_categories))]

# (3) Show a line chart of sales for the selected items
st.write("### (3) show a line chart of sales for the selected items in (2)")
if not filtered_data.empty:
    st.header("Sales Trend")
    # Pivot data for line chart
    pivot_data = filtered_data.pivot_table(index="Order_Date", columns="Sub_Category", values="Sales", aggfunc="sum").reset_index()
    # Melt the pivot table so Altair can handle multiple lines
    melted_data = pivot_data.melt(id_vars=["Order_Date"], var_name="Sub_Category", value_name="Sales")
    # Create line chart with trend line using Altair
    chart = alt.Chart(melted_data).mark_line().encode(
        x='Order_Date:T',
        y='Sales:Q',
        color='Sub_Category:N'
    ).properties(
        width=700,
        height=400
    )
    # Add trend line (using LOESS smoothing)
    trend = chart.transform_loess(
        'Order_Date', 'Sales', groupby=['Sub_Category']
    ).mark_line(strokeDash=[4,2], color='black', opacity=0.3)
    # Combine chart and trend line
    st.altair_chart(chart + trend, use_container_width=True)
else:
    st.write("Please select Sub_Category to view the chart.")

# (4) Show three metrics
st.write("### (4) show three metrics for the selected items in (2): total sales, total profit, and overall profit margin (%)")
st.write("### (5) use the delta option in the overall profit margin metric to show the difference between the overall average profit margin (all products across all categories)")
if not filtered_data.empty:
    total_sales = filtered_data["Sales"].sum()
    total_profit = filtered_data["Profit"].sum()
    overall_profit_margin = (total_profit / total_sales) * 100

    # Calculate the overall average profit margin (all products across all categories)
    overall_avg_profit_margin = (df["Profit"].sum() / df["Sales"].sum()) * 100

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Profit", f"${total_profit:,.2f}")
    with col3:
        st.metric(
            "Overall Profit Margin (%)",
            f"{overall_profit_margin:.2f}%",
            delta=f"{overall_profit_margin - overall_avg_profit_margin:.2f}%",  # (5) Use delta to show the difference
        )
else:
    st.write("Please select Sub_Category to view metrics.")
