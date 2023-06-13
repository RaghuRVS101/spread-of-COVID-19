import csv
import random
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from sim_parameters import TRASITION_PROBS, HOLDING_TIMES
import helper

def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    countries_data = pd.read_csv(countries_csv_name)
    countries_data = countries_data[countries_data['country'].isin(countries)]
    countries_data['sample_population'] = (countries_data['population'] * sample_ratio).astype(float)

    age_groups = ['less_5', '5_to_14', '15_to_24', '25_to_64', 'over_65']

    timeline_data = []
    person_id = 0

    for _, row in countries_data.iterrows():
        for age_group in age_groups:
            num_people = int(row[age_group] * row['sample_population'] / 100)
            for _ in range(num_people):
                timeline_data.append({
                    'person_id': person_id,
                    'age_group': age_group,
                    'country': row['country'],
                    'timeline': []
                })
                person_id += 1

    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    num_days = (end_datetime - start_datetime).days + 1

    for person in timeline_data:
        age_group = person['age_group']
        state = 'H'
        staying_days = 0

        for day in range(num_days):
            if staying_days > 0:
                staying_days -= 1
            else:
                state_probs = TRASITION_PROBS[age_group][state]
                state = random.choices(list(state_probs.keys()), list(state_probs.values()))[0]
                staying_days = HOLDING_TIMES[age_group][state] - 1

            person['timeline'].append({
                'date': (start_datetime + timedelta(days=day)).strftime('%Y-%m-%d'),
                'state': state,
                'staying_days': staying_days
            })

    with open('a3-covid-simulated-timeseries.csv', 'w', newline='') as csvfile:
        fieldnames = ['person_id', 'age_group_name', 'country', 'date', 'state', 'staying_days']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for person in timeline_data:
            for day_data in person['timeline']:
                writer.writerow({
                    'person_id': person['person_id'],
                    'age_group_name': person['age_group'],
                    'country': person['country'],
                    'date': day_data['date'],
                    'state': day_data['state'],
                    'staying_days': day_data.get('staying_days', 0)
                })

    summary_data = []

    for date in pd.date_range(start=start_date, end=end_date, freq='D'):
        date_str = date.strftime('%Y-%m-%d')
        for country in countries:
            country_data = countries_data[countries_data['country'] == country]
            state_counts = {'H': 0, 'I': 0, 'S': 0, 'D': 0, 'M': 0, 'date': date_str, 'country': country}
            for person in timeline_data:
                if person['country'] == country:
                    day_data = person['timeline'][(date - start_datetime).days]
                    state_counts[day_data['state']] += 1
            summary_data.append(state_counts)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('a3-covid-summary-timeseries.csv', index=False)
    helper.create_plot(summary_df, countries)