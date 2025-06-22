"""
Massachusetts Carbon Fee & Dividend Simulator

This script runs an interactive web application using Streamlit to simulate the
financial impacts of a carbon fee and dividend policy in Massachusetts.

It allows users to adjust various policy parameters and see the projected
effects on state revenue, GHG emissions, and household dividends in real-time.

For a full explanation of the policy concepts, model assumptions, and
mathematical formulas, please refer to the README.md file.
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="MA Carbon Dividend Simulator", layout="wide")

st.title("Massachusetts Carbon Fee & Dividend Simulator")
st.markdown("Use the sidebar to adjust policy parameters and see the results update in real-time. See `README.md` for full documentation.")


# --- SECTION 1: USER INPUTS IN SIDEBAR ---
# All user-adjustable parameters are defined here. The default values are
# based on sources and justifications outlined in the project's README.md.
st.sidebar.header("Policy Inputs")

# --- Core fee parameters ---
st.sidebar.subheader("Carbon Fee")
start_year = 2027
years = st.sidebar.slider("Years to simulate", 4, 30, 10,
                          help="Number of years to run the simulation, starting from 2027.")
years_range = list(range(start_year, start_year + years))

fee_start = st.sidebar.number_input("Starting carbon fee $/t (2027)",
                                    min_value=0.0, value=30.0, step=1.0,
                                    help="The initial fee per metric ton of CO2-equivalent in the first year.")

fee_increment = st.sidebar.number_input("Annual fee increment ($/t)",
                                        min_value=0.0, value=10.0, step=1.0,
                                        help="The amount the fee increases each year. A steady increase provides a predictable market signal.")

elasticity = st.sidebar.slider("Price elasticity of demand (-)",
                               min_value=-1.0, max_value=-0.05, value=-0.30, step=0.05,
                               help="How much emissions demand falls in response to a price increase. E.g., -0.3 means a 10% price increase causes a 3% demand drop.")

# --- Baseline emissions & population ---
st.sidebar.subheader("State Demographics & Emissions")
base_emissions = st.sidebar.number_input("Covered GHG emissions 2027 (MMT CO2-e)",
                                         min_value=1.0, value=55.0, step=1.0,
                                         help="Projected baseline greenhouse gas emissions (in Million Metric Tons) for the policy's start year.")

pop_2025 = st.sidebar.number_input("Population 2025 (millions)",
                                   min_value=0.1, value=7.206, step=0.001, format="%.3f",
                                   help="Baseline population for Massachusetts.")

pop_growth = st.sidebar.slider("Annual population growth rate (%)",
                               min_value=-1.0, max_value=2.0, value=0.25, step=0.05,
                               help="Assumed annual rate of population change.")

# --- Fiscal parameters ---
st.sidebar.subheader("Revenue Allocation")
admin_skim = st.sidebar.slider("Admin skim (% of revenue)",
                               min_value=0.0, max_value=10.0, value=2.0, step=0.1,
                               help="Percentage of gross revenue set aside for administrative costs.")

ej_skim = st.sidebar.slider("EJ carve-out (% of revenue)",
                            min_value=0.0, max_value=20.0, value=5.0, step=0.1,
                            help="Percentage of gross revenue dedicated to an Environmental Justice fund.")

low_income_bonus = st.sidebar.slider("Low-income bonus (%)",
                                     min_value=0.0, max_value=100.0, value=30.0, step=5.0,
                                     help="The supplemental percentage bonus paid to qualified low-income households.")

# --- Universal Carbon Income (CPF) parameters ---
st.sidebar.subheader("Climate Prosperity Fund (CPF)")
cpf_diversion = st.sidebar.slider("CPF diversion (% of dividend pool)",
                                  min_value=0.0, max_value=50.0, value=20.0, step=1.0,
                                  help="Percentage of the annual dividend pool diverted to capitalize the CPF.")

cpf_target = st.sidebar.number_input("CPF target principal ($ billion)",
                                     min_value=0.0, value=5.0, step=0.5,
                                     help="The fund balance goal. Once met, diversions stop and it pays a Universal Carbon Income.")

cpf_return = st.sidebar.slider("CPF real return (%/yr)",
                               min_value=0.0, max_value=10.0, value=5.0, step=0.5,
                               help="The assumed real (after-inflation) annual investment return for the CPF.")

# --- SECTION 2: SIMULATION LOGIC ---
# This section takes the user inputs and runs the year-by-year simulation.

# --- Derived constants and initial values ---
admin_rate = admin_skim / 100.0
ej_rate = ej_skim / 100.0
cpf_diversion_rate = cpf_diversion / 100.0
bonus_rate = low_income_bonus / 100.0
cpf_return_rate = cpf_return / 100.0

# --- Initialize data containers and loop variables ---
results = []
emissions = base_emissions
fee = fee_start
cpf_balance = 0.0  # in billions of dollars
population = pop_2025 # in millions

# This factor approximates the number of "full shares" in the dividend system.
# It's a simplification based on the assumption that children (~20% of pop)
# receive a half-share (0.5), so the total number of shares is less than the
# total population. (80% * 1) + (20% * 0.5) = 0.9.
shares_factor = 0.9

for year in years_range:
    # --- Annual Calculations ---

    # 1. Determine fee for the current year
    if year > start_year:
        fee += fee_increment

    # 2. Calculate emissions reduction based on the fee increase
    # (Skip for the first year as we start with base_emissions)
    if year > start_year:
        prev_fee = fee - fee_increment
        # See formula in README.md for this calculation
        emissions *= (1 + elasticity * ((fee - prev_fee) / prev_fee))

    # 3. Calculate gross revenue (in billions of dollars)
    revenue = (fee * emissions) / 1000.0

    # 4. Calculate the total pool of money available for dividends
    # after taking the admin and EJ skims off the top.
    dividend_raw = revenue * (1 - admin_rate - ej_rate)

    # 5. Handle the Climate Prosperity Fund (CPF) logic
    diversion_to_cpf = 0.0 # in billions of dollars
    # If the CPF hasn't hit its target, divert a portion of the dividend pool.
    if cpf_balance < cpf_target:
        diversion_to_cpf = dividend_raw * cpf_diversion_rate
        # The remaining pool is the final dividend for this year.
        dividend_pool = dividend_raw - diversion_to_cpf
    else:
        # If the target is met, no more money is diverted.
        dividend_pool = dividend_raw

    # The CPF balance grows from its own returns and any new diversion.
    cpf_balance = cpf_balance * (1 + cpf_return_rate) + diversion_to_cpf

    # 6. Calculate per-person dividend payments
    # Total shares are based on the population (in millions).
    total_shares = shares_factor * population
    # To get the correct $/person value, we must convert units consistently:
    # ($billions * 1e9) / (shares_in_millions * 1e6)
    adult_dividend = (dividend_pool * 1_000) / total_shares if total_shares > 0 else 0
    child_dividend = adult_dividend / 2.0
    low_income_dividend = adult_dividend * (1 + bonus_rate)

    # 7. Store the results for this year
    results.append({
        "Year": year,
        "Fee $/t": round(fee, 2),
        "Emissions (MMT)": round(emissions, 2),
        "Revenue ($bn)": round(revenue, 2),
        "Dividend pool ($bn)": round(dividend_pool, 2),
        "Adult dividend ($/yr)": round(adult_dividend, 0),
        "Child dividend ($/yr)": round(child_dividend, 0),
        "Low-income adult dividend ($/yr)": round(low_income_dividend, 0),
        "CPF balance ($bn)": round(cpf_balance, 2)
    })

    # 8. Update population for the next year's loop
    population *= (1 + pop_growth / 100.0)

# --- SECTION 3: DISPLAY OUTPUTS ---
# Display the results in a table and charts.

df = pd.DataFrame(results).set_index("Year")

st.subheader("Summary Table")
st.dataframe(df.style.format("{:,.2f}"), use_container_width=True)

# --- Charts ---
st.subheader("Dividend & Emissions Trajectory")
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot dividends on the primary y-axis
color = 'tab:blue'
ax1.set_xlabel('Year')
ax1.set_ylabel('Annual Adult Dividend ($)', color=color)
ax1.plot(df.index, df["Adult dividend ($/yr)"], color=color, marker='o', label='Adult Dividend')
ax1.plot(df.index, df["Low-income adult dividend ($/yr)"], color='tab:green', linestyle='--', label='Low-Income Adult Dividend')
ax1.tick_params(axis='y', labelcolor=color)
ax1.legend(loc='upper left')

# Create a second y-axis for emissions
ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Emissions (MMT CO2-e)', color=color)
ax2.plot(df.index, df["Emissions (MMT)"], color=color, marker='o', linestyle=':', label='Emissions')
ax2.tick_params(axis='y', labelcolor=color)
ax2.legend(loc='upper right')

fig.tight_layout()
st.pyplot(fig)


st.subheader("Revenue Allocation & CPF Growth")
fig2, ax = plt.subplots(figsize=(10, 6))
# Stacked bar chart for revenue allocation
ax.bar(df.index, df["Dividend pool ($bn)"], label='Dividend Pool ($bn)')
ax.bar(df.index, df["Revenue ($bn)"] - df["Dividend pool ($bn)"], bottom=df["Dividend pool ($bn)"], label='Skims & Diversions ($bn)')
ax.set_xlabel("Year")
ax.set_ylabel("Revenue & Allocation ($bn)")
ax.legend()

# Line chart for CPF balance on a secondary axis
ax2 = ax.twinx()
ax2.plot(df.index, df["CPF balance ($bn)"], color='purple', marker='o', label='CPF Balance ($bn)')
ax2.set_ylabel("CPF Balance ($bn)", color='purple')
ax2.tick_params(axis='y', labelcolor='purple')
ax2.legend(loc='upper right')

st.pyplot(fig2)

st.caption("Note: All monetary values beyond the fee rate are shown in constant dollars (i.e., real terms).") 