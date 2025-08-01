# Importing required modules and libraries 
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import sim_parameters
import helper



#importing the requried transition probabilities and holding times from the sim parameters 
Trans_chances = sim_parameters.TRANSITION_PROBS
locking_period = sim_parameters.HOLDING_TIMES



#making constants for the file names of output csv files 
OUTPUT_SIMULATED_DATA_CSV = 'a2-covid-simulated-timeseries.csv'
OUTPUT_SUMMARY_DATA_CSV = 'a2-covid-summary-timeseries.csv'


#a small function to get the number of days between the given date range 
def date_range(start_date,end_date):
    startDate = datetime.strptime(start_date, '%Y-%m-%d').date()
    endDate = datetime.strptime(end_date, '%Y-%m-%d').date()
    return (endDate - startDate).days


# function used to process the data and generate the sample population of different age slabs 
def data_preprocessing(countries_csv_name, countries, sample_ratio):
    df = pd.read_csv(countries_csv_name)
    df = df.loc[df['country'].isin(countries)]
    df['population'] = df['population'] // sample_ratio
    age_columns = ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']
    df[age_columns] = df[age_columns].apply(lambda x: round(x * df['population'] / 100))
    df['total_samples'] = df[age_columns].sum(axis=1)
    return df


# this function is used for simulating the covid for a single person 
def covid_simulation_for_single_person(person_id, age_slab, country, start_date, time_span):
    datums = pd.date_range(start=start_date, periods=time_span)
    state = 'H'  # Initial state
    forhead_state = 'H' #previous state 
    resting_time = 0 #the holding period 
    span_of_period = [] 
    #for loop iterating in the time span we are having 
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


# function that simuates the covid for the given set of countries 
def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    # Sampling population data
    inhabitants_data = data_preprocessing(countries_csv_name, countries, sample_ratio)
    time_span = date_range(start_date, end_date) + 1

    # list that stores the time series of each person 
    span_of_period_list = []
    
    person_id = 0
    for i, row in inhabitants_data.iterrows():
        for age_slab in ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']:
            # Converting the populations age slab into integer
            age_group_population = int(row[age_slab])
            
            #looping through the population for every age slab 
            for _ in range(age_group_population):
                # Simulate individual and append the results to the list
                span_of_period_list.extend(covid_simulation_for_single_person(person_id, age_slab, row['country'], start_date, time_span))
                person_id += 1

    # convert list to dataframe 
    span_of_period_df = pd.DataFrame(span_of_period_list, columns=["person_id", "age_group_name", "country", "date", "state", "resting_time", "forhead_state"])

    # Saving the simulated time series in csv format
    span_of_period_df.to_csv(OUTPUT_SIMULATED_DATA_CSV, index=False)

    # Creating summary for each time series 
    summary_data = span_of_period_df.groupby(['date', 'country', 'state']).size().unstack(fill_value=0).reset_index()

    # Ensuring all states ['H', 'I', 'S', 'M', 'D'] are present, even if counts are 0
    for s in ['H', 'I', 'S', 'M', 'D']:
        if s not in summary_data.columns:
            summary_data[s] = 0  # Add missing state column with 0 values

    summary_data = summary_data[['date', 'country', 'H', 'I', 'S', 'M', 'D']]  # Reorder the columns
    
    # Saving the summary of timeseries in csv format 
    summary_data.to_csv(OUTPUT_SUMMARY_DATA_CSV, index=False)

    # ploting the graph with output summary file 
    helper.create_plot(OUTPUT_SUMMARY_DATA_CSV, countries)

