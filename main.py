import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
def load_data():
    data = pd.read_csv("Agent Time On Status Template_Jul 10 2025 11_38,Jun 29 2025-Jul 5 2025_MIN15.csv")
    data['Start Time'] = pd.to_datetime(data['Start Time'].str[:-6])
    data['End Time'] = pd.to_datetime(data['End Time'].str[:-6])

    time_cols = ['Available Time', 'Handling Time', 'Wrap Up Time', 'Working Offline Time',
                 'On Break Time', 'Busy Time', 'Logged In Time', 'Offering Time']
    for col in time_cols:
        data[col] = pd.to_timedelta(data[col])

    return data

# Data aggregation
def aggregate_data(data):
    summary = data.groupby('Agent').agg({
        'Available Time': 'sum', 'Handling Time': 'sum', 'Wrap Up Time': 'sum',
        'Working Offline Time': 'sum', 'On Break Time': 'sum', 'Busy Time': 'sum',
        'Logged In Time': 'sum'
    })
    summary['Productive Time'] = summary['Handling Time'] + summary['Wrap Up Time'] + summary['Busy Time']
    summary['Productivity %'] = round((summary['Productive Time'] / summary['Logged In Time']).round(2) * 100, 2)
    return summary.reset_index()

def main():
    # Dashboard creation
    st.title('📊 Call Center Agent Dashboard')

    # Load and process data
    data = load_data()
    summary = aggregate_data(data)

    # Agent Productivity Bar Chart
    st.header('Agent Productivity (%)')
    prod_chart = px.bar(summary.sort_values('Productivity %', ascending=False),
                        x='Productivity %', y='Agent', orientation='h',
                        color='Productivity %', text='Productivity %',
                        labels={'Productivity %':'Productivity (%)'}, height=500)
    st.plotly_chart(prod_chart)

    # Logged-in vs Productive Time Stacked Bar Chart
    st.header('Logged-in vs Productive Time')
    summary['Logged In Hours'] = round(summary['Logged In Time'].dt.total_seconds() / 3600, 2)
    summary['Productive Hours'] = round(summary['Productive Time'].dt.total_seconds() / 3600, 2)
    stacked_df = summary.melt(id_vars=['Agent'], value_vars=['Logged In Hours', 'Productive Hours'],
                            var_name='Type', value_name='Hours')
    stacked_chart = px.bar(stacked_df, x='Hours', y='Agent', color='Type', orientation='h', height=500)
    st.plotly_chart(stacked_chart)

    # Break & Offline Time Scatter Plot
    st.header('Break & Offline Time Analysis')
    summary['Break Hours'] = round(summary['On Break Time'].dt.total_seconds() / 3600, 2)
    summary['Offline Hours'] = round(summary['Working Offline Time'].dt.total_seconds() / 3600, 2)
    scatter_chart = px.scatter(summary, x='Break Hours', y='Offline Hours', size='Logged In Hours',
                            color='Agent', labels={'Break Hours':'Break Time (hrs)', 'Offline Hours':'Offline Time (hrs)'},
                            height=500)
    st.plotly_chart(scatter_chart)

    # Daily Activity Heatmap
    st.header('Daily Activity Patterns')
    data['Date'] = data['Start Time'].dt.date
    daily_data = data.groupby(['Date', 'Agent']).agg({'Logged In Time':'sum'}).reset_index()
    daily_data['Logged In Hours'] = round(daily_data['Logged In Time'].dt.total_seconds() / 3600)
    heatmap_data = daily_data.pivot(index='Agent', columns='Date', values='Logged In Hours').fillna(0)
    heatmap_chart = px.imshow(heatmap_data, labels=dict(x="Date", y="Agent", color="Hours"), height=600)
    st.plotly_chart(heatmap_chart)

if __name__ == "__main__":
    main()
