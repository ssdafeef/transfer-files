import pandas as pd
import numpy as np
import random

NUM_CITIES = 50

languages = ["Arabic", "English", "French", "Spanish", "Dari", "Urdu", "Swahili"]
skills = ["Carpentry", "IT", "Healthcare", "Plumbing", "Teaching",
          "Construction", "Agriculture", "Logistics", "Retail", "Engineering"]
cost_levels = ["Low", "Medium", "High"]

data = []

for i in range(NUM_CITIES):
    data.append([
        i,
        f"City_{i}",
        random.choice(languages),
        random.randint(2500, 3500),                 # capacity
        ",".join(random.sample(skills, 3)),        # job demand as string
        round(np.random.uniform(0.03, 0.15), 2),    # unemployment_rate
        random.choice(cost_levels),
        round(np.random.uniform(0, 1), 2),          # diaspora_support_index
        round(np.random.uniform(0.5, 1.0), 2)       # integration_policy_score
    ])

df = pd.DataFrame(data, columns=[
    "city_id",
    "city_name",
    "primary_language",
    "capacity",
    "job_demand",
    "unemployment_rate",
    "cost_level",
    "diaspora_support_index",
    "integration_policy_score"
])

df.to_csv("synthetic_cities_25.csv", index=False)

print("25 cities dataset created successfully!")