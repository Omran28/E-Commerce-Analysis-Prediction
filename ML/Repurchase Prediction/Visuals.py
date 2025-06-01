import matplotlib.pyplot as plt


def features_day_graph(data):
    plt.figure(figsize=(12, 8))
    for i, feature in enumerate(['TotalQuantity', 'UniqueCustomers', 'DiscountCount'], 1):
        plt.subplot(3, 1, i)
        plt.plot(data['Day'], data[feature], label=feature)
        plt.xlabel('Day of Year')
        plt.ylabel(feature)
        plt.grid(True)
        plt.legend()

    plt.tight_layout()
    plt.show()


# Models
def random_forest_pred_graph(data, X_test, rf_pred):
    plt.figure(figsize=(10, 6))
    plt.plot(data['Day'], data['Smoothed_DailyRevenue'], label='Smoothed Daily Revenue', color='orange')
    plt.scatter(X_test['Day'], rf_pred, label='Random Forest Predicted Revenue', color='green', alpha=0.5)
    plt.xlabel('Day of Year')
    plt.ylabel('Daily Revenue')
    plt.title('Random Forest Revenue Prediction')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def xgboost_pred_graph(data, X_test, xgb_pred):
    plt.figure(figsize=(10, 6))
    plt.plot(data['Day'], data['Smoothed_DailyRevenue'], label='Smoothed Daily Revenue', color='orange')
    plt.scatter(X_test['Day'], xgb_pred, label='XGBoost Predicted Revenue', color='blue', alpha=0.5)
    plt.xlabel('Day of Year')
    plt.ylabel('Daily Revenue')
    plt.title('XGBoost Revenue Prediction')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Anomalies
def anomalies_data_graph(data, anomalies):
    plt.figure(figsize=(10, 6))
    plt.scatter(data['Day'], data['Smoothed_DailyRevenue'], label='Revenue', alpha=0.5)
    plt.scatter(anomalies['Day'], anomalies['DailyRevenue'], color='red', label='Anomalies', alpha=0.8)
    plt.xlabel('Day of Year')
    plt.ylabel('Daily Revenue')
    plt.title('Detected Anomalies in Smoothed Revenue')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Raw with smoothed data
def raw_smoothed_data_graph(data):
    plt.figure(figsize=(12,6))
    plt.plot(data['Day'], data['DailyRevenue'], label='Raw Daily Revenue', marker='o')
    plt.plot(data['Day'], data['Smoothed_DailyRevenue'], label='Smoothed Daily Revenue', marker='x')
    plt.xlabel('Day of Year')
    plt.ylabel('Revenue')
    plt.title('Raw vs Smoothed Daily Revenue Over Days')
    plt.legend()
    plt.grid(True)
    plt.show()