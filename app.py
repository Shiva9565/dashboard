import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(layout="wide")
st.title("Recommendation Timeline Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Extract countries and years
    countries = df['Country'].dropna().unique()
    years = [2026, 2027, 2028, 2029, 2030]

    # Country selector
    selected_country = st.selectbox("Select a Country", sorted(countries))

    dff = df[df['Country'] == selected_country].copy()
    dff = dff.dropna(subset=['Recommendation No'])

    # Sort and group
    dff = dff.sort_values(by=['Initiative', 'Recommendation No'])
    label_map = {}
    y_labels = []
    y_pos = 0

    for initiative in dff['Initiative'].unique():
        y_labels.append((y_pos, initiative))
        y_pos += 1
        subset = dff[dff['Initiative'] == initiative]
        for _, row in subset.iterrows():
            short = row['Recommendation \n(Short)']
            if isinstance(short, str) and len(short) > 90:
                short = short[:90] + '...'
            label = f"{row['Recommendation No']} | {short}"
            label_map[(initiative, row['Recommendation No'])] = (y_pos, label)
            y_labels.append((y_pos, label))
            y_pos += 1
        y_pos += 1

    # Create plot
    data = []
    for (initiative, rec), (y, label) in label_map.items():
        row = dff[(dff['Initiative'] == initiative) & (dff['Recommendation No'] == rec)].iloc[0]
        for year in years:
            if str(row.get(str(year), 0)) == '1':
                data.append(go.Scatter(
                    x=[year],
                    y=[y],
                    mode='markers+text',
                    marker=dict(size=20, color='deepskyblue',line=dict(width=2, color='white')),
                    text=[rec],
                    textposition='middle center',
                    showlegend=False
                ))

    fig = go.Figure(data=data)
    fig.update_layout(
        yaxis=dict(
            tickvals=[y for y, _ in y_labels if _ not in dff['Initiative'].unique()],
            ticktext=[label for y, label in y_labels if label not in dff['Initiative'].unique()],
            autorange='reversed',
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            tickvals=years,
            title='Year (2026–2030)',
            side='top'
        ),
        height=40 * len(y_labels),
        margin=dict(l=300, r=50, t=60, b=30),
        title=f"{selected_country} – Recommendation Timeline"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Please upload a CSV file to proceed.")
