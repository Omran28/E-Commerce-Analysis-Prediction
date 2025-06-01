import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import entropy
from sqlalchemy import create_engine

from Preprocessing import *

# Database connection string
connection_string = (
    f"mssql+pyodbc://localhost/new_database"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes"
    "&Encrypt=no"
)
engine = create_engine(connection_string)


# Read data
data = pd.read_sql(features_query, engine)

data.drop(columns=['customer_id'], inplace=True)

# Drop non-numeric or ID columns (e.g., customer_id)
numeric_df = data.select_dtypes(include=[np.number])

# Step 1: Normalize all features [0,1]
scaler = MinMaxScaler()
normalized = pd.DataFrame(scaler.fit_transform(numeric_df), columns=numeric_df.columns)

# Step 2: Compute Variance (importance by spread)
variance_scores = normalized.var()

# Step 3: Compute Entropy (importance by unpredictability)
entropy_scores = normalized.apply(lambda col: entropy(np.histogram(col, bins=10, range=(0,1), density=True)[0]), axis=0)

# Step 4: Normalize variance and entropy to get weights
var_weights = variance_scores / variance_scores.sum()
ent_weights = entropy_scores / entropy_scores.sum()

# Step 5: Combine weights (equal importance)
combined_weights = (var_weights + ent_weights) / 2

# Step 6: Display sorted weights
weights_df = pd.DataFrame({
    'VarianceWeight': var_weights,
    'EntropyWeight': ent_weights,
    'FinalWeight': combined_weights
}).sort_values('FinalWeight', ascending=False)

print(weights_df)
