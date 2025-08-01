import streamlit as st
import pandas as pd
import os
import plotly.express as px
from sim_parameters import *  # Importing simulation constants
from assign3 import run   # Importing the run function from your assignment file
from datetime import datetime
import time  # Import time for progress simulation

# Set default values
SAMPLE_RATIO = 1e5
START_DATE = '2021-04-01'
END_DATE = '2022-04-30'
CSV_FILE = 'a2-countries.csv'

#paths for the files 
summary_file = 'a2-covid-summary-timeseries.csv'
image_file = 'a2-covid-simulation.png'
# Function to check if the file exists
def check_file_exists(file_name):
    return os.path.exists(file_name)

# Load countries from CSV
if check_file_exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    countries_list = df['country'].unique().tolist()
else:
    countries_list = []
    st.error(f"Oops! The file '{CSV_FILE}' doesn't seem to be available. Please check the file path.")

# Streamlit inputs
st.title('Covid Spread Simulation')

# Sample Ratio input
SAMPLE_RATIO = st.number_input('Sample Ratio', value=SAMPLE_RATIO, format='%f')

# Date range inputs
try:
    START_DATE = st.date_input('Start Date', value=datetime.strptime(START_DATE, '%Y-%m-%d'))
    END_DATE = st.date_input('End Date', value=datetime.strptime(END_DATE, '%Y-%m-%d'))
    if END_DATE < START_DATE:
        st.warning("Please make sure the End Date is after the Start Date.")
except Exception as e:
    st.error("There seems to be an issue with the date format. Please check and try again.")

# Countries multi-select
SELECTED_COUNTRIES = st.multiselect('Select Countries', options=countries_list)

# Option to choose between interactive plot or static image
plot_option = st.radio("Select graph type:", ('Static Image', 'Interactive Plot'))

# Set up session state to track if the "Run" button was clicked and to hold previous input values
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False  # Tracks if the user has run the simulation
    st.session_state.previous_sampling_ratio = SAMPLE_RATIO  # Store previous sample ratio
    st.session_state.previous_starting_date = START_DATE  # Store previous start date
    st.session_state.previous_end_date = END_DATE  # Store previous end date
    st.session_state.previously_selected_countries_for_input = []  # To store the previous selected countries
# Function to run the simulation
def run_simulation():
    if os.path.exists(image_file):
        os.remove(image_file)
    # Run the simulation (this should generate both the summary CSV and the static image)
    run(countries_csv_name=CSV_FILE, 
        countries=SELECTED_COUNTRIES, 
        start_date=str(START_DATE), 
        end_date=str(END_DATE), 
        sample_ratio=SAMPLE_RATIO)

# "Run" button to start the simulation
if st.button('Run'):
    # Clear previous outputs
    st.session_state.simulation_run = False  # Reset simulation run state

    if not SELECTED_COUNTRIES:
        st.warning("Please select at least Two country to run the simulation.")
    else:
        st.session_state.simulation_run = True  # Mark the simulation as run
        placeholder = st.empty()  # Create a placeholder for the running message
        placeholder.write("Running simulation...")  # Display running message

        # Simulate a loading period
        for _ in range(100):
            time.sleep(0.02)  # Simulate time taken by the run function
            placeholder.progress(_ + 1)  # Update the progress

        try:
            run_simulation()  # Call the function to run the simulation
            # Store current states in session
            st.session_state.previously_selected_countries_for_input = SELECTED_COUNTRIES
            st.session_state.previous_sampling_ratio = SAMPLE_RATIO
            st.session_state.previous_starting_date = START_DATE
            st.session_state.previous_end_date = END_DATE
        except Exception as e:
            st.error("Oops! Something went wrong while running the simulation. Please check your input values and try again.")

# Check if any input values have changed since the last run
changed = (
    SELECTED_COUNTRIES != st.session_state.previously_selected_countries_for_input or
    SAMPLE_RATIO != st.session_state.previous_sampling_ratio or
    START_DATE != st.session_state.previous_starting_date or
    END_DATE != st.session_state.previous_end_date
)

# Only proceed if the "Run" button was clicked and files exist
if st.session_state.simulation_run:
    if changed:
        placeholder = st.empty()  # Create a new placeholder for the running message
        placeholder.write("Running simulation...")  # Display running message

        # Simulate a loading period
        for _ in range(100):
            time.sleep(0.02)  # Simulate time taken by the run function
            placeholder.progress(_ + 1)  # Update the progress

        try:
            run_simulation()  # Run the simulation again if inputs have changed
            # Store current states in session after rerun
            st.session_state.previously_selected_countries_for_input = SELECTED_COUNTRIES
            st.session_state.previous_sampling_ratio = SAMPLE_RATIO
            st.session_state.previous_starting_date = START_DATE
            st.session_state.previous_end_date = END_DATE
        except Exception as e:
            st.error("There was an issue running the simulation with the new settings. Please verify your inputs.")

    # Check for the existence of files after running the simulation
    if check_file_exists(summary_file) and check_file_exists(image_file):
        if plot_option == 'Interactive Plot':
            # Load the summary CSV
            summary_df = pd.read_csv(summary_file)

            # Interactive Plotly graph for the selected countries
            st.header(f"COVID-19 States Over Time for {', '.join(SELECTED_COUNTRIES)}")

            try:
                for country in SELECTED_COUNTRIES:
                    country_data = summary_df[summary_df['country'] == country]

                        # Plot with Plotly
                    fig = px.line(country_data, 
                                      x='date', 
                                      y=['H', 'I', 'S', 'M', 'D'], 
                                      title=f'COVID-19 State Progression in {country}',
                                      labels={'value': 'Number of People', 'variable': 'State'},
                                      template='plotly_dark')

                    st.plotly_chart(fig)
            except Exception as e:
                st.error("It seems there was a problem displaying the graph. Please ensure the data is available and correctly formatted.")

        elif plot_option == 'Static Image':
            # Display the static image that was generated by the `run` function
            st.header(f"COVID-19 States Over Time for {', '.join(SELECTED_COUNTRIES)}")
            st.image(image_file)

            # Indicate that the static image has been displayed
            st.session_state.static_image_displayed = True  # Flag that static image has been shown
    else:
        st.error("It looks like the simulation didn't generate the necessary files. Please try running it again.")

# Store the current states in session
st.session_state.previously_selected_countries_for_input = SELECTED_COUNTRIES
st.session_state.previous_sampling_ratio = SAMPLE_RATIO
st.session_state.previous_starting_date = START_DATE
st.session_state.previous_end_date = END_DATE

