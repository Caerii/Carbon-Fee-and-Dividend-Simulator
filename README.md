# Massachusetts Carbon Fee & Dividend Simulator

This is an interactive application for simulating the financial impacts of a state-level carbon fee and dividend policy in Massachusetts. It is designed for policymakers, advocates, and the public to explore how different policy designs affect state revenue, greenhouse gas emissions, and household dividends.

The simulation is built with Python using the Streamlit library.

## Table of Contents
- [How to Run the Simulator](#how-to-run-the-simulator)
- [Core Concepts Explained](#core-concepts-explained)
  - [What is a Carbon Fee and Dividend?](#what-is-a-carbon-fee-and-dividend)
  - [Climate Prosperity Fund (Universal Carbon Income)](#climate-prosperity-fund-universal-carbon-income)
  - [Equity and Affordability Mechanisms](#equity-and-affordability-mechanisms)
- [The Simulation Model](#the-simulation-model)
  - [Key Assumptions & Parameters](#key-assumptions--parameters)
  - [Core Formulas](#core-formulas)
- [Limitations of the Model](#limitations-of-the-model)
- [How to Contribute](#how-to-contribute)

## How to Run the Simulator

To run this application on your local machine, follow these steps:

1.  **Prerequisites:** Ensure you have Python 3.9 or newer installed.

2.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

3.  **Install Dependencies:** The required packages are listed in `requirements.txt`. Install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    ```bash
    streamlit run carbon_dividend_sim.py
    ```
    A new tab should open in your web browser with the running application.

## Core Concepts Explained

This simulator models a policy with several key components designed to ensure it is both effective at reducing emissions and economically fair for residents.

### What is a Carbon Fee and Dividend?
A carbon fee and dividend is a market-based climate policy with two main parts:
1.  **The Fee:** A fee (or tax) is applied to fossil fuels based on the amount of carbon dioxide (CO₂) they will emit when burned. This fee is typically collected at the first point of sale in the economy (e.g., from fuel importers and distributors). The rising fee makes cleaner energy sources more cost-competitive, incentivizing a gradual, economy-wide shift away from fossil fuels.
2.  **The Dividend:** The money collected from the fee (the revenue) is returned directly to households on an equal, per-person basis. Most proposals give children a half-share. Because everyone receives an equal share, and higher-income households tend to have a larger carbon footprint, most low- and middle-income families receive more in dividends than they pay in increased energy costs, making them financially better off.

### Climate Prosperity Fund (Universal Carbon Income)
Instead of returning 100% of the revenue each year, this model includes an option to divert a portion of the revenue into a **Climate Prosperity Fund (CPF)**. This is a state-managed investment fund, similar in principle to the [Alaska Permanent Fund](https://pfd.alaska.gov/).

-   **Capitalization Phase:** A percentage of carbon revenue is transferred into the CPF until it reaches a target principal (e.g., $5 billion).
-   **Payout Phase:** Once the target is reached, the CPF's investment returns are paid out annually to every resident as a **Universal Carbon Income (UCI)**. This creates a permanent source of public wealth that continues to pay dividends even after carbon fee revenues decline as the state decarbonizes.

### Equity and Affordability Mechanisms
To ensure the policy benefits all residents, especially the most vulnerable, two other mechanisms are included:

-   **Low-Income Bonus:** Qualified low-income households receive a percentage "bonus" on top of their standard dividend. This provides extra financial protection against rising energy costs.
-   **Environmental Justice (EJ) Carve-Out:** A percentage of the gross carbon revenue is set aside into a dedicated trust fund. This fund finances decarbonization and climate resilience projects (e.g., insulation, heat pumps, public transit) directly within designated Environmental Justice communities.

## The Simulation Model

The following section details the specific assumptions, default values, and mathematical formulas used in the simulator.

### Key Assumptions & Parameters

The parameters below can be adjusted in the application's sidebar. The default values are based on recent legislative proposals and publicly available data.

| Parameter                      | Default | Source / Justification                                                                                                                                     |
| ------------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Starting Carbon Fee (2027)** | $30/ton | A common starting point in recent US state-level carbon pricing bills (e.g., MA H.2810, 2019). Balances impact with economic feasibility.                 |
| **Annual Fee Increment**       | +$10/t  | A predictable, modest annual increase provides a clear market signal for long-term investment in clean energy without causing sudden price shocks.         |
| **Price Elasticity of Demand** | -0.30   | A mid-range academic estimate. It means for every 10% increase in the price of carbon, demand (emissions) is assumed to fall by 3%.                     |
| **Covered GHG Emissions (2027)** | 55 MMT  | Based on Massachusetts' 2021 energy-related CO₂ emissions (~56 MMT, [U.S. EIA](https://fred.stlouisfed.org/series/EMISSCO2ENNA)) plus other GHGs, with a projected reduction before the policy starts. |
| **Population (2025)**          | 7.206 M | Based on 2024 population estimates ([World Population Review](https://www.worldpopulationreview.com/states/massachusetts-population)).                            |
| **Annual Population Growth**   | 0.25%   | Reflects recent, modest population growth trends in Massachusetts.                                                                                       |
| **Administrative Skim**        | 2%      | An estimate of the funds required by the Department of Revenue for program implementation, based on fiscal notes for prior bills.                      |
| **EJ Carve-Out**               | 5%      | A common figure in recent climate proposals to ensure dedicated funding for frontline communities.                                                       |
| **Low-Income Bonus**           | 30%     | Provides a significant boost to make the policy highly progressive. The exact value is a key design choice for legislators.                               |
| **CPF Diversion Rate**         | 20%     | A rate that allows for meaningful CPF capitalization without dramatically reducing near-term dividends.                                                    |
| **CPF Target Principal**       | $5 bn   | A target principal large enough to generate a meaningful Universal Carbon Income stream in perpetuity.                                                     |
| **CPF Real Return**            | 5%/yr   | A conservative, long-term real rate of return (i.e., after inflation) for a diversified investment portfolio.                                            |

### Core Formulas

The simulation proceeds year-by-year according to the formulas below.

1.  **Emissions Reduction:** For each year after the first, emissions are reduced based on the fee increase and the price elasticity.
    \[ E_t = E_{t-1} \times \left( 1 + \epsilon \times \frac{F_t - F_{t-1}}{F_{t-1}} \right) \]
    *   *E<sub>t</sub>*: Emissions in year *t*
    *   *ε*: Price elasticity of demand

2.  **Gross Revenue:**
    \[ R_t = F_t \times E_t \]
    *   *R<sub>t</sub>*: Gross revenue in year *t*
    *   *F<sub>t</sub>*: Carbon fee in year *t*

3.  **Dividend Pool (before CPF diversion):**
    \[ D_{t, \text{raw}} = R_t \times (1 - s_{\text{admin}} - s_{\text{ej}}) \]
    *   *s<sub>admin</sub>*, *s<sub>ej</sub>*: Admin and EJ skim rates

4.  **Final Dividend Pool (after CPF diversion):**
    \[ D_t = D_{t, \text{raw}} \times (1 - d_{\text{cpf}}) \]
    *   *d<sub>cpf</sub>*: CPF diversion rate (this diversion only occurs if the CPF balance is below its target).

5.  **Per-Share Dividend:** The model assumes children (<18) receive a half-share. We approximate the total number of shares (*S<sub>t</sub>*) as 90% of the total population, a simplification based on census data.
    \[ \text{Adult Dividend}_t = \frac{D_t}{S_t} \]

6.  **Climate Prosperity Fund Balance:**
    \[ \text{CPF}_t = \text{CPF}_{t-1} \times (1 + r) + \text{Diversion}_t \]
    *   *r*: Real return on CPF assets

## Limitations of the Model
-   **Simplicity:** This is a high-level macroeconomic model. It does not capture complex interactions between different sectors of the economy.
-   **Static Elasticity:** The model uses a single, constant price elasticity for the entire economy. In reality, different sectors (e.g., transportation, electricity) will respond differently to price changes.
-   **No General Equilibrium Effects:** The model does not account for how changes in energy prices or dividend payments might affect overall economic growth, inflation, or employment.

## How to Contribute
Contributions are welcome! Please feel free to submit a pull request or open an issue to suggest improvements, new features, or bug fixes. 