import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(layout="wide")
st.title("Recommendation Timeline Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Define column indices
    COL_COUNTRY = 0
    COL_INITIATIVE = 2
    COL_REC_NO = 3
    COL_REC_SHORT = 4
    COL_YEARS = [5, 6, 7, 8, 9]
    YEARS = [2026, 2027, 2028, 2029, 2030]

    # Extract countries
    countries = df.iloc[:, COL_COUNTRY].dropna().unique()

    # Country selector
    selected_country = st.selectbox("Select a Country", sorted(countries))

    dff = df[df.iloc[:, COL_COUNTRY] == selected_country].copy()
    dff = dff.dropna(subset=[df.columns[COL_REC_NO]])

    # Sort by initiative and recommendation number
    dff = dff.sort_values(by=[df.columns[COL_INITIATIVE], df.columns[COL_REC_NO]])
    
    label_map = {}
    y_labels = []
    y_pos = 0

    for initiative in dff.iloc[:, COL_INITIATIVE].unique():
        y_labels.append((y_pos, initiative))
        y_pos += 1
        subset = dff[dff.iloc[:, COL_INITIATIVE] == initiative]
        for _, row in subset.iterrows():
            short = row.iloc[COL_REC_SHORT]
            if isinstance(short, str) and len(short) > 90:
                short = short[:90] + '...'
            rec_no = row.iloc[COL_REC_NO]
            label = f"{rec_no} | {short}"
            label_map[(initiative, rec_no)] = (y_pos, label)
            y_labels.append((y_pos, label))
            y_pos += 1
        y_pos += 1

    # Create plot
    data = []
    for (initiative, rec), (y, label) in label_map.items():
        row = dff[(dff.iloc[:, COL_INITIATIVE] == initiative) & 
                  (dff.iloc[:, COL_REC_NO] == rec)].iloc[0]
        for col_idx, year in zip(COL_YEARS, YEARS):
            if str(row.iloc[col_idx]) == '1':
                data.append(go.Scatter(
                    x=[year],
                    y=[y],
                    mode='markers+text',
                    marker=dict(size=20, color='deepskyblue', line=dict(width=2, color='white')),
                    text=[rec],
                    textposition='middle center',
                    showlegend=False
                ))

    fig = go.Figure(data=data)
    fig.update_layout(
        yaxis=dict(
            tickvals=[y for y, _ in y_labels if _ not in dff.iloc[:, COL_INITIATIVE].unique()],
            ticktext=[label for y, label in y_labels if label not in dff.iloc[:, COL_INITIATIVE].unique()],
            autorange='reversed',
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            tickvals=YEARS,
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
