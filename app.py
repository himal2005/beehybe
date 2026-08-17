import streamlit as st
import pandas as pd
import numpy as np

# Set page title and layout
st.set_page_config(
    page_title="My Streamlit App",
    page_icon="🚀",
    layout="centered"
)

# Title and description
st.title("🚀 Simple Streamlit Web App")
st.write("Welcome! This is a simple interactive web application built entirely in Python.")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to section:", ["Home", "Data Visualizer", "User Input"])

# Section 1: Home
if page == "Home":
    st.header("Home Page")
    st.write("Streamlit allows you to turn Python scripts into interactive web apps in minutes.")
    st.info("Use the sidebar on the left to navigate between different sections!")

# Section 2: Data Visualizer
elif page == "Data Visualizer":
    st.header("📊 Interactive Data Visualizer")
    
    st.write("Generate random data and visualize it on the fly:")
    
    # Slider control for data points
    num_points = st.slider("Select number of data points:", min_value=10, max_value=200, value=50)
    
    # Generate random line chart data
    chart_data = pd.DataFrame(
        np.random.randn(num_points, 3),
        columns=['Metric A', 'Metric B', 'Metric C']
    )
    
    st.line_chart(chart_data)
    
    # Toggle to view raw data table
    if st.checkbox("Show raw data table"):
        st.dataframe(chart_data)

# Section 3: User Input
elif page == "User Input":
    st.header("📝 Interactive Form")
    
    with st.form("user_info_form"):
        name = st.text_input("Enter your name:")
        role = st.selectbox("Select your role:", ["Developer", "Data Scientist", "Student", "Other"])
        satisfaction = st.slider("How much do you like Python?", 1, 10, 8)
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.success(f"Hello **{name}**! Your response has been recorded.")
            st.json({
                "Name": name,
                "Role": role,
                "Python Score": satisfaction
            })