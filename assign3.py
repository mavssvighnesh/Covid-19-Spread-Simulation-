# Importing required modules and libraries 
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import sim_parameters
import helper

# Importing the required transition probabilities and holding times from the sim_parameters
Trans_chances = sim_parameters.TRANSITION_PROBS
locking_period = sim_parameters.HOLDING_TIMES

# Constants for the output CSV file names
OUTPUT_SIMULATED_DATA_CSV = 'a2-covid-simulated-timeseries.csv'
OUTPUT_SUMMARY_DATA_CSV = 'a2-covid-summary-timeseries.csv'

# Function to get the number of days between the given date range
def date_range(start_date, end_date):
    startDate = datetime.strptime(start_date, '%Y-%m-%d').date()
    endDate = datetime.strptime(end_date, '%Y-%m-%d').date()
    return (endDate - startDate).days

# Function to process the data and generate the sample population of different age slabs
def data_preprocessing(countries_csv_name, countries, sample_ratio):
    df = pd.read_csv(countries_csv_name)
    df = df[df['country'].isin(countries)]  # Filter for selected countries
    df['population'] = df['population'] // sample_ratio
    age_columns = ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']
    df[age_columns] = df[age_columns].apply(lambda x: round(x * df['population'] / 100))
    df['total_samples'] = df[age_columns].sum(axis=1)
    return df

# Simulates COVID-19 progression for a single individual
def covid_simulation_for_single_person(person_id, age_slab, country, start_date, time_span):
    datums = pd.date_range(start=start_date, periods=time_span)
    state = 'H'  # Initial state
    forhead_state = 'H'  # Previous state
    resting_time = 0  # The holding period
    span_of_period = []

    # Loop through each day in the time span
    for i in range(time_span):
        if resting_time > 0:
            resting_time -= 1
        else:
            trans_probs = Trans_chances[age_slab][state]
            backward_state = np.random.choice(list(trans_probs.keys()), p=list(trans_probs.values()))
            resting_time = locking_period[age_slab][backward_state]
            forhead_state, state = state, backward_state

        span_of_period.append([person_id, age_slab, country, datums[i].strftime('%Y-%m-%d'), state, resting_time, forhead_state])

    return span_of_period

# Runs the simulation for the selected set of countries
def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    # Sampling population data
    inhabitants_data = data_preprocessing(countries_csv_name, countries, sample_ratio)
    time_span = date_range(start_date, end_date) + 1

    # List that stores the time series of each person
    span_of_period_list = []
    
    person_id = 0
    for _, row in inhabitants_data.iterrows():
        for age_slab in ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']:
            age_group_population = int(row[age_slab])  # Convert population of each age slab to an integer
            for _ in range(age_group_population):
                # Simulate individual and append the results to the list
                span_of_period_list.extend(covid_simulation_for_single_person(person_id, age_slab, row['country'], start_date, time_span))
                person_id += 1

    # Convert the list to a DataFrame
    span_of_period_df = pd.DataFrame(span_of_period_list, columns=["person_id", "age_group_name", "country", "date", "state", "resting_time", "forhead_state"])

    # Save the simulated time series data in CSV format
    span_of_period_df.to_csv(OUTPUT_SIMULATED_DATA_CSV, index=False)

    # Create a summary for each time series by grouping by date, country, and state
    summary_data = span_of_period_df.groupby(['date', 'country', 'state']).size().unstack(fill_value=0).reset_index()

    # Ensure all states ['H', 'I', 'S', 'M', 'D'] are present, adding missing columns with 0 values if needed
    for state in ['H', 'I', 'S', 'M', 'D']:
        if state not in summary_data.columns:
            summary_data[state] = 0  # Add missing state column with 0 values

    # Reorder the columns to ensure consistent ordering
    summary_data = summary_data[['date', 'country', 'H', 'I', 'S', 'M', 'D']]

    # Save the summary data to a CSV file
    summary_data.to_csv(OUTPUT_SUMMARY_DATA_CSV, index=False)

    # Plot the graph using the output summary file
    helper.create_plot(OUTPUT_SUMMARY_DATA_CSV, countries)
