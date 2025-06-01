import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import joblib
from pycaret.classification import *
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
data = pd.read_sql(query_test, engine)

# Features list
features = [
    "CustomerTenure",      # Customer Account Duration (days since registration)
    "SessionCount",        # Total number of customer sessions
    "WishlistItems",       # Total number of unique wishlist items (all-time)
    "TotalSpent",          # Total amount of money spent by the customer
    "ActiveDays",          # Number of distinct days customer placed orders (activity span)
    "TotalOrders",         # Total number of orders placed
    "OrdersPerMonth",      # Average number of orders placed per month
    "SuccessfulPayments",  # Number of successful payment transactions
    "WishlistCount",       # Number of wishlist additions in the last 60 days (recent interest)
    "AvgRating",           # Average customer rating given in reviews
    "TotalReturns",        # Total number of returned orders
    "ActiveMonths",        # Number of active months in customer order history
    "OrderCompletionRate", # Ratio of completed orders (delivered/shipped) to total orders
    "AvgOrderValue",       # Average order value (monetary)
    "DeliveryRate",        # Proportion of orders delivered successfully
    "AvgSessionDuration",  # Average session duration in minutes
    "CancelRate",          # Proportion of orders canceled
    "DaysSinceLastOrder"   # Days elapsed since last order date
]


# Adjust OrdersPerMonth values
data.loc[data['TotalOrders'] == 0, 'OrdersPerMonth'] = 0
data.loc[data['TotalOrders'] == 1, 'OrdersPerMonth'] = 1

# Replace all NaNs in the DataFrame with 0
data.fillna(0, inplace=True)


# Target Conversion
data['CustomerScoreClass'] = (data['CustomerScore'] >= 0.6).astype(int)



# Splitting data
# Shuffle full dataset
data_shuffled = data.sample(frac=1, random_state=42).reset_index(drop=True)

# Separate classes
data_pos = data_shuffled[data_shuffled['CustomerScoreClass'] == 1]
data_neg = data_shuffled[data_shuffled['CustomerScoreClass'] == 0]

# Define how many from each class in test data
n_test_each = 25  # 25 pos + 25 neg = 50 total test data

# Create test data
test_pos = data_pos.iloc[:n_test_each]
test_neg = data_neg.iloc[:n_test_each]
test_data = pd.concat([test_pos, test_neg]).sample(frac=1, random_state=42).reset_index(drop=True)

# Create training data
train_pos = data_pos.iloc[n_test_each:]
train_neg = data_neg.iloc[n_test_each:]
train_data = pd.concat([train_pos, train_neg]).sample(frac=1, random_state=42).reset_index(drop=True)

# Verify counts
# print("Train set size:", len(train_data))
# print("Test set size:", len(test_data))
# print("\nTrain class distribution:\n", train_data['CustomerScoreClass'].value_counts())
# print("\nTest class distribution:\n", test_data['CustomerScoreClass'].value_counts())



# Save customer_id for later use in testing
customer_ids = test_data['customer_id'].copy()

# Drop unnecessary columns
train_data.drop(columns=['CustomerScore', 'customer_id'], inplace=True)

# View Correlation score
# correlations = train_data.corr()[['CustomerScoreClass']].sort_values(by='CustomerScoreClass', ascending=False)
# print(correlations)

# Correlation
# features_correlation(data)


# ---------------------------------------------------------------------------------------
# Automation
# Setup with classification data
exp_name = setup(data=train_data, target='CustomerScoreClass', session_id=42, verbose=False)

# create a random forest model
rf_model = create_model('rf')

# Plot feature importance
plot_model(rf_model, plot='feature')

# Evaluate model performance
evaluate_model(rf_model)



# Testing
# Saving customer id and true label
customer_ids_test = test_data['customer_id'].values
true_labels = test_data['CustomerScoreClass'].values

# Make predictions using the trained model
predictions = predict_model(rf_model, data=test_data.drop(columns=['customer_id']))

# Combine results with prediction probability
results = pd.DataFrame({
    'customer_id': test_data['customer_id'].values,
    'prediction': predictions['prediction_label'].values,
    'true_label': test_data['CustomerScoreClass'].values,
    'prediction_proba': predictions['prediction_score'].values
})

# Classification report
print(classification_report(results['true_label'], results['prediction']))

# Generate confusion matrix
cm = confusion_matrix(results['true_label'], results['prediction'])

# define class names
class_names = sorted(results['true_label'].unique())

# Using seaborn heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.show()

# View results
# print(results.head())



# Save results to csv
# results.to_csv("customer_predictions.csv", index=False)

# Save the model
# save_model(rf_model, 'repurchase_model_rf')
