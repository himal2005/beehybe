import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Set page title and layout
st.set_page_config(page_title="Function Plotter", layout="centered")

st.title("📈 Interactive Function Plotter")
st.write("Visualize mathematical functions dynamically.")

# Sidebar controls for customization
st.sidebar.header("Plot Settings")

# Dropdown for common mathematical functions
function_option = st.sidebar.selectbox(
    "Select a function to plot:",
    [
        "Sine: sin(x)",
        "Cosine: cos(x)",
        "Polynomial: x^2 - 4x + 3",
        "Exponential: exp(x)",
        "Damped Sine Wave: exp(-0.2*x) * sin(2*x)",
    ],
)

# Range and resolution sliders
x_min = st.sidebar.number_input("X Minimum", value=-10.0, step=1.0)
x_max = st.sidebar.number_input("X Maximum", value=10.0, step=1.0)
points = st.sidebar.slider(
    "Resolution (number of points)", min_value=100, max_value=2000, value=500
)

# Generate X values
x = np.linspace(x_min, x_max, points)

# Calculate Y values based on selection
if function_option == "Sine: sin(x)":
    y = np.sin(x)
    title = r"$y = \sin(x)$"
elif function_option == "Cosine: cos(x)":
    y = np.cos(x)
    title = r"$y = \cos(x)$"
elif function_option == "Polynomial: x^2 - 4x + 3":
    y = x**2 - 4 * x + 3
    title = r"$y = x^2 - 4x + 3$"
elif function_option == "Exponential: exp(x)":
    y = np.exp(x)
    title = r"$y = e^x$"
elif function_option == "Damped Sine Wave: exp(-0.2*x) * sin(2*x)":
    y = np.exp(-0.2 * x) * np.sin(2 * x)
    title = r"$y = e^{-0.2x} \cdot \sin(2x)$"

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(x, y, label=function_option, color="#1f77b4", linewidth=2)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_title(title, fontsize=14)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()

# Display plot in Streamlit app
st.pyplot(fig)