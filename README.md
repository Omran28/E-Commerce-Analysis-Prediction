# 🛒 E-Commerce Analytics & Machine Learning Prediction

## 📖 Table of Contents  
- [🗄️ SQL Server & Azure Integration](#-sql-server--azure-integration)  
- [🛡️ Azure Security & Reliability](#-azure-security--reliability)  
- [📊 SQL Data Analysis & Queries](#-sql-data-analysis--queries)  
- [📈 Power BI Dashboards & Microsoft Fabric](#-power-bi-dashboards--microsoft-fabric)  
- [🤖 Machine Learning Models](#-machine-learning-models)  

---

## 🗄️ SQL Server & Azure Integration  
This project begins with a comprehensive **E-commerce database** built on **SQL Server**, which was successfully deployed and linked to an **Azure SQL Database** for scalable cloud storage and management.

### Key Highlights:
- Created and configured the database schema and tables on SQL Server.
- Migrated and synchronized the database to Azure SQL for cloud accessibility.
- Established seamless connectivity between local SQL Server and Azure SQL.

### Visuals:
![Database Schema](images/sql_schema.png)  
*Database schema representing customer, orders, and products tables.*

![Azure SQL Setup](images/azure_sql_setup.png)  
*Azure portal screenshot showing database instance and configuration.*

---

## 🛡️ Azure Security & Reliability  
Ensuring data protection and system resilience, multiple security and operational features were applied on Azure SQL Database.

### Key Features Implemented:
- Configured **Azure Firewall** rules and exceptions for controlled access.
- Enabled **Transparent Data Encryption (TDE)** for data-at-rest protection.
- Enforced **TLS protocols** for secure data in transit.
- Deployed **DDoS protection** to prevent denial-of-service attacks.
- Implemented **Automated Backups** and **Failover Groups** for high availability.

### Visuals:
![Azure Firewall](images/azure_firewall.png)  
*Azure Firewall configuration overview.*

![Failover Groups](images/failover_groups.png)  
*Setup of Failover Groups for disaster recovery.*

---

## 📊 SQL Data Analysis & Queries  
A total of **12 intensive SQL queries** were developed and executed to analyze sales, customer behavior, and product trends.

### Breakdown:
- **6 Basic Queries** covering key metrics like total sales, average order value, and active customers.
- **6 Advanced Queries** incorporating complex joins, window functions, and aggregations for deeper insights.

### Visuals:
![SQL Query Sample](images/sql_query_sample.png)  
*Example of a complex query calculating monthly active customers.*

![Query Results](images/query_results.png)  
*Sample results from advanced analysis queries.*

---

## 📈 Power BI Dashboards & Microsoft Fabric  
The analyzed data was connected to **Power BI** to create dynamic dashboards that visualize customer behavior, sales trends, and product performance.

### Key Points:
- Connected Power BI directly to Azure SQL Database for real-time data refresh.
- Developed multiple interactive dashboards with filters and drill-downs.
- Integrated Power BI with **Microsoft Fabric** to enable enterprise-grade data analytics.

### Visuals:
![Power BI Dashboard](images/powerbi_dashboard.png)  
*Dashboard visualizing customer segmentation and sales funnel.*

![Microsoft Fabric Integration](images/microsoft_fabric.png)  
*Microsoft Fabric workspace showing linked Power BI reports.*

---

## 🤖 Machine Learning Models  

### Overview  
This section presents three key ML models developed to enhance business decisions and customer engagement in the e-commerce domain:

- **Customer Repurchase Prediction:** A high-accuracy classification model predicting customers' likelihood of repurchasing.
- **Customer Segmentation:** Unsupervised clustering to identify distinct customer groups based on purchasing patterns.
- **Product Recommendation:** Collaborative filtering-based system to suggest personalized products.

---

### 🔄 Repurchase Prediction Model 📊

#### 🔍 Overview  
An **AI-driven customer repurchase prediction system** leveraging a **Random Forest classifier** trained on rich transactional and behavioral features. It predicts customer repurchase likelihood, enabling targeted marketing and improving retention.

#### 🚀 Features  
- **Advanced Feature Selection:** Utilizes combined Variance and Entropy scores to robustly select the most informative features.  
- **Normalization:** Applies Min-Max scaling for consistent feature ranges.  
- **Weighted Feature Engineering:** Features such as Total Spent, Orders Per Month, Successful Payments, and Active Days are engineered and weighted based on variance and entropy scores.  
- **Dynamic Thresholding:** Thresholds optimized through correlation analysis and distribution examination to maximize prediction accuracy.  
- **Robust Modeling:** Employs a Random Forest classifier with 10-fold cross-validation to ensure generalization and stability.  
- **Seamless Integration:** Connected with SQL Server database enabling dynamic querying and model updates.

#### 🏗 Model Summary  
- **Random Forest Classifier:** Handles non-linearity and complex feature interactions inherent in customer behavior.  
- **Feature Engineering:** Custom features that capture customer purchase frequency, monetary value, and engagement periods.  
- **Normalization & Weighting:** Ensures feature uniformity and emphasizes important features via entropy-weighted scoring.  
- **Cross-Validation:** 10-fold cross-validation confirms robustness and avoids overfitting.

#### 📈 Performance  
| Metric       | Score     |  
|--------------|-----------|  
| Accuracy     | 98.57%    |  
| AUC          | 1.0       |  
| Recall       | 100%      |  
| Precision    | 97.78%    |  
| F1 Score     | 98.82%    |  
| Cohen’s Kappa| 97.02%    |  
| MCC          | 97.21%    |  

- Test set accuracy of 98% with only 1 misclassification out of 50 samples, demonstrating excellent predictive power.

#### 📊 Classification Report  
| Class               | Precision | Recall | F1-Score | Support |  
|---------------------|-----------|--------|----------|---------|  
| Repurchase = No (0)  | 1.00      | 0.96   | 0.98     | 25      |  
| Repurchase = Yes (1) | 0.96      | 1.00   | 0.98     | 25      |  

#### 🛠 Technologies Used  
- **Python** – Core programming language  
- **PyCaret** – Simplified ML workflow and model training  
- **Scikit-learn** – Model utilities and evaluation metrics  
- **SQLAlchemy & pyodbc** – Database connectivity and querying  
- **Pandas & NumPy** – Data manipulation and preprocessing  

### Visuals:  
![Repurchase Prediction ROC](images/repurchase_prediction_roc.png)  
*ROC curve showcasing model’s classification performance.*  

![Feature Importance](images/repurchase_feature_importance.png)  
*Feature importance scores highlighting key drivers for repurchase prediction.*

---

### Additional ML Models  
- **Customer Segmentation:** Clustering customers into distinct groups to tailor marketing and engagement.  
- **Product Recommendation:** Collaborative filtering-based recommendation system to boost cross-selling and customer satisfaction.

### Visuals:  
![Customer Segmentation](images/customer_segmentation.png)  
*Customer clusters visualized using dimensionality reduction.*  

![Product Recommendation](images/product_recommendation.png)  
*Example personalized product recommendations.*

---

## 📝 Summary  
This project delivers a full end-to-end data analytics and machine learning pipeline tailored for e-commerce. It integrates secure cloud-based database management, in-depth data analysis, interactive visualizations, and predictive modeling — empowering data-driven decisions that enhance business growth and customer engagement.

---
