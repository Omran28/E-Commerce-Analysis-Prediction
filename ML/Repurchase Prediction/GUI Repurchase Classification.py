import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy import create_engine
from pycaret.classification import predict_model, load_model
from Preprocessing import *

# Colors and styles
BG_COLOR = "#f0f4f8"
ACCENT_COLOR = "#4a90e2"
POS_COLOR = "#28a745"
NEG_COLOR = "#dc3545"
TEXT_COLOR = "#333333"
FRAME_BG = "#ffffff"

# Database connection
connection_string = (
    f"mssql+pyodbc://localhost/new_database"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes"
    "&Encrypt=no"
)

engine = create_engine(connection_string)

# Load model
model = load_model('repurchase_model_rf')

# Feature importance data
feature_importance = {
    'Total Spent': 0.76,
    'Total Orders': 0.69,
    'Orders Per Month': 0.69,
    'Successful Payments': 0.68,
    'Active Days': 0.67,
    'Active Months': 0.46,
    'Session Count': 0.39,
}



def get_customer_features(customer_id, query):
    query = query.format(customer_id=customer_id)
    df = pd.read_sql(query, engine)
    if df.empty:
        raise ValueError(f"No data found for customer ID: {customer_id}")
    return df


def predict_customer(customer_id):
    data = get_customer_features(customer_id, query_test_gui)
    data.loc[data['TotalOrders'] == 0, 'OrdersPerMonth'] = 0
    data.loc[data['TotalOrders'] == 1, 'OrdersPerMonth'] = 1
    data.fillna(0, inplace=True)
    X = data.drop(columns=['customer_id', 'CustomerScore', 'CustomerScoreClass'], errors='ignore')

    result = predict_model(model, data=X)
    prediction = int(result['prediction_label'].values[0] == 1)
    proba = result['prediction_score'].values[0]
    return prediction, proba, X.iloc[0]


# GUI Setup
root = tk.Tk()
root.title("Customer Repurchase Classification")
root.geometry("650x580")
root.configure(bg=BG_COLOR)
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=1)

# Title
title_font = ("Segoe UI", 18, "bold")
tk.Label(root, text="Customer Repurchase Classification", font=title_font, fg=ACCENT_COLOR, bg=BG_COLOR).grid(row=0,
                                                                                                              column=0,
                                                                                                              pady=15)

# Input Frame
input_frame = tk.Frame(root, bg=BG_COLOR)
input_frame.grid(row=1, column=0, pady=10, sticky="ew")
input_frame.columnconfigure(1, weight=1)

tk.Label(input_frame, text="Enter Customer ID:", font=("Segoe UI", 12), bg=BG_COLOR).grid(row=0, column=0, padx=5,
                                                                                          sticky="w")
customer_id_entry = tk.Entry(input_frame, font=("Segoe UI", 12), width=12)
customer_id_entry.grid(row=0, column=1, padx=5, sticky="w")

# Result Frame
result_frame = tk.Frame(root, bg=FRAME_BG, bd=2, relief="groove")
result_frame.grid(row=2, column=0, pady=10, padx=15, sticky="ew")

result_var = tk.StringVar()
result_label = tk.Label(result_frame, textvariable=result_var, font=("Segoe UI", 14, "bold"), bg=FRAME_BG)
result_label.pack(padx=10, pady=10)


def set_result_text(customer_id, label, proba):
    color = POS_COLOR if label == "Repurchase Likely" else NEG_COLOR
    icon = "✓" if label == "Repurchase Likely" else "✗"
    result_var.set(f"{icon} Customer ID: {customer_id} → Prediction: {label}\nProbability: {proba:.2%}")
    result_label.config(fg=color)


# Features Frame
feature_frame = tk.Frame(root, bg=FRAME_BG, bd=2, relief="sunken")
feature_frame.grid(row=3, column=0, padx=15, pady=10, sticky="nsew")
feature_frame.columnconfigure(0, weight=1)
feature_frame.rowconfigure(1, weight=1)

tk.Label(feature_frame, text="Most Useful Features (Correlation with Target):", font=("Segoe UI", 12, "bold"),
         bg=FRAME_BG).grid(row=0, column=0, sticky="w", padx=10, pady=5)

cols = ("Feature", "Correlation")
tree = ttk.Treeview(feature_frame, columns=cols, show='headings', height=10)
tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

for i, (feat, corr) in enumerate(sorted(feature_importance.items(), key=lambda x: abs(x[1]), reverse=True)):
    tag = 'oddrow' if i % 2 else 'evenrow'
    tree.insert("", "end", values=(feat, f"{corr:.2f}"), tags=(tag,))

tree.tag_configure('oddrow', background='#e8f0fe')
tree.tag_configure('evenrow', background='#ffffff')


def on_predict_click():
    customer_id = customer_id_entry.get().strip()
    if not customer_id:
        messagebox.showwarning("Input Error", "Please enter a Customer ID.")
        return
    try:
        prediction, proba, features = predict_customer(customer_id)
        label = "Repurchase Likely" if prediction == 1 else "Repurchase Unlikely"
        set_result_text(customer_id, label, proba)
        print("====== Prediction Debug Info ======")
        print(f"Customer ID: {customer_id}")
        print(f"Prediction: {prediction} → {label}")
        print(f"Probability: {proba:.2%}")
        print("\nInput Features Used:")
        print(features.to_string())
        print("===================================")
    except Exception as e:
        result_var.set("")
        messagebox.showerror("Prediction Error", str(e))

# Button
# Define the hover colors
hover_bg = "#0052cc"  # darker blue for hover
normal_bg = ACCENT_COLOR  # original button background color

def on_enter(event):
    event.widget.config(bg=hover_bg)

def on_leave(event):
    event.widget.config(bg=normal_bg)

# Create the button
predict_btn = tk.Button(root, text="Predict Repurchase",
                        font=("Segoe UI", 12, "bold"),
                        fg="white",
                        bg=normal_bg,
                        activeforeground="white",
                        activebackground=hover_bg,
                        relief="flat",
                        padx=10, pady=5)
predict_btn.grid(row=4, column=0, pady=15)
predict_btn.config(command=on_predict_click)

# Bind hover events
predict_btn.bind("<Enter>", on_enter)
predict_btn.bind("<Leave>", on_leave)

root.mainloop()
