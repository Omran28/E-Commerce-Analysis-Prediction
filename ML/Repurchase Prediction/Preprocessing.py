import seaborn as sns
import matplotlib.pyplot as plt


def moving_average(data, column, window_size):
    data["Smoothed_DailyRevenue"] = data[column].rolling(window=window_size, center=True).mean()
    return data


def features_correlation(data):
    sns.heatmap(data.corr(), annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Feature Correlation Matrix")
    plt.show()


# Get feature importances
# feature_importances = rf_model.feature_importances_
# print("Length of feature importances:", len(feature_importances))

# Create DataFrame
# feat_imp_df = pd.DataFrame({
#     'Feature': processed_features,
#     'Importance': feature_importances
# }).sort_values(by='Importance', ascending=False)
#
# print(feat_imp_df)



old_query = """
WITH 
-- Aggregate core customer order metrics
CustomerMetrics AS (
    SELECT 
        o.customer_id,
        COUNT(o.id) AS TotalOrders,
        DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS ActiveDaysRange,
        CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0 AS ActiveMonths,
        COUNT(o.id) / NULLIF(CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0, 0) AS OrdersPerMonth,
        DATEDIFF(DAY, MAX(o.order_date), '2025-05-07') AS DaysSinceLastOrder,
        SUM(CASE WHEN o.status IN ('delivered', 'shipped') THEN 1 ELSE 0 END) AS CompletedOrders
    FROM orders o
    GROUP BY o.customer_id
),

-- Average customer review rating
ReviewMetrics AS (
    SELECT 
        customer_id,
        AVG(rating) AS AvgRating
    FROM reviews
    GROUP BY customer_id
),

-- Count of wishlist additions within last 60 days
WishlistMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistCount
    FROM wishlists
    WHERE added_date >= DATEADD(DAY, -60, '2025-05-07')
    GROUP BY customer_id
),

-- Count of successful payments per customer
PaymentMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS SuccessfulPayments
    FROM payments
    GROUP BY customer_id
),

-- Additional order-level aggregated stats
CustomerOrderStats AS (
    SELECT 
        o.customer_id,
        COUNT(*) AS TotalOrdersStats,
        COUNT(DISTINCT CAST(o.order_date AS DATE)) AS ActiveDays,
        SUM(o.total_amount) AS TotalSpent,
        AVG(o.total_amount) AS AvgOrderValue,
        COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 1.0 / COUNT(*) AS DeliveryRate,
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) * 1.0 / COUNT(*) AS CancelRate
    FROM orders o
    GROUP BY o.customer_id
),

-- Return statistics per customer
CustomerReturns AS (
    SELECT 
        o.customer_id,
        COUNT(r.id) AS TotalReturns,
        COUNT(r.id) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0) AS ReturnRate
    FROM orders o
    LEFT JOIN returns r ON o.id = r.order_id
    GROUP BY o.customer_id
),

-- Total wishlist items per customer (all time)
CustomerWishlists AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistItems
    FROM wishlists
    GROUP BY customer_id
),

-- Customer session counts and average duration
CustomerSessions AS (
    SELECT 
        customer_id,
        COUNT(*) AS SessionCount,
        AVG(DATEDIFF(MINUTE, session_start, session_end)) AS AvgSessionDuration
    FROM customer_sessions
    GROUP BY customer_id
),

-- Customer tenure in days
CustomerBase AS (
    SELECT
        c.id AS customer_id,
        DATEDIFF(DAY, c.registration_date, '2025-05-07') AS CustomerTenure
    FROM customers c
),

-- Merge core metrics and payments and order stats for score calculation
AllMetrics AS (
    SELECT 
        cm.customer_id,
        cm.TotalOrders,
        cm.ActiveDaysRange AS ActiveDays,
        cm.ActiveMonths,
        cm.OrdersPerMonth,
        cm.DaysSinceLastOrder,
        ISNULL(pm.SuccessfulPayments, 0) AS SuccessfulPayments,
        ISNULL(co.TotalSpent, 0) AS TotalSpent
    FROM CustomerMetrics cm
    LEFT JOIN PaymentMetrics pm ON cm.customer_id = pm.customer_id
    LEFT JOIN CustomerOrderStats co ON cm.customer_id = co.customer_id
),

-- Normalization stats for all features used in CustomerScore
NormalizationStats AS (
    SELECT
        MIN(ActiveMonths) AS MinActiveMonths, MAX(ActiveMonths) AS MaxActiveMonths,
        MIN(OrdersPerMonth) AS MinOrdersPerMonth, MAX(OrdersPerMonth) AS MaxOrdersPerMonth,
        MIN(DaysSinceLastOrder) AS MinDaysSinceLastOrder, MAX(DaysSinceLastOrder) AS MaxDaysSinceLastOrder,
        MIN(SuccessfulPayments) AS MinSuccessfulPayments, MAX(SuccessfulPayments) AS MaxSuccessfulPayments,
        MIN(TotalOrders) AS MinTotalOrders, MAX(TotalOrders) AS MaxTotalOrders,
        MIN(ActiveDays) AS MinActiveDays, MAX(ActiveDays) AS MaxActiveDays,
        MIN(TotalSpent) AS MinTotalSpent, MAX(TotalSpent) AS MaxTotalSpent
    FROM AllMetrics
)

SELECT
    cb.customer_id,

    -- Core features
    cm.TotalOrders,
    cm.ActiveMonths,
    cm.OrdersPerMonth,
    cm.DaysSinceLastOrder,
    CAST(cm.CompletedOrders AS FLOAT) / NULLIF(cm.TotalOrders, 0) AS OrderCompletionRate,
    COALESCE(rm.AvgRating, 0) AS AvgRating,
    COALESCE(wm.WishlistCount, 0) AS WishlistCount,
    COALESCE(pm.SuccessfulPayments, 0) AS SuccessfulPayments,

    -- Extended features
    co.TotalSpent,
    co.AvgOrderValue,
    co.DeliveryRate,
    co.CancelRate,
    co.ActiveDays,
    cr.TotalReturns,
    cr.ReturnRate,
    cw.WishlistItems,
    cs.SessionCount,
    cs.AvgSessionDuration,
    cb.CustomerTenure,

    -- CustomerScore based on normalized key metrics
    CAST(
        0.22 * (am.ActiveMonths - ns.MinActiveMonths) / NULLIF(ns.MaxActiveMonths - ns.MinActiveMonths, 0) +
        0.18 * (am.TotalOrders - ns.MinTotalOrders) / NULLIF(ns.MaxTotalOrders - ns.MinTotalOrders, 0) +
        0.18 * (am.ActiveDays - ns.MinActiveDays) / NULLIF(ns.MaxActiveDays - ns.MinActiveDays, 0) +
        0.17 * (am.SuccessfulPayments - ns.MinSuccessfulPayments) / NULLIF(ns.MaxSuccessfulPayments - ns.MinSuccessfulPayments, 0) +
        0.15 * (am.OrdersPerMonth - ns.MinOrdersPerMonth) / NULLIF(ns.MaxOrdersPerMonth - ns.MinOrdersPerMonth, 0) +
        0.10 * (1.0 - (am.DaysSinceLastOrder - ns.MinDaysSinceLastOrder) / NULLIF(ns.MaxDaysSinceLastOrder - ns.MinDaysSinceLastOrder, 0)) +
        0.10 * (am.TotalSpent - ns.MinTotalSpent) / NULLIF(ns.MaxTotalSpent - ns.MinTotalSpent, 0)
    AS FLOAT) AS CustomerScore

FROM CustomerBase cb
LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id
LEFT JOIN AllMetrics am ON cb.customer_id = am.customer_id
CROSS JOIN NormalizationStats ns;

"""



# Calculating avg entropy-variance score for target equation
features_query = """

WITH 
-- Aggregate core customer order metrics
CustomerMetrics AS (
    SELECT 
        o.customer_id,
        COUNT(o.id) AS TotalOrders,
        DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS ActiveDaysRange,
        CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0 AS ActiveMonths,
        COUNT(o.id) / NULLIF(CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0, 0) AS OrdersPerMonth,
        DATEDIFF(DAY, MAX(o.order_date), '2025-05-07') AS DaysSinceLastOrder,
        SUM(CASE WHEN o.status IN ('delivered', 'shipped') THEN 1 ELSE 0 END) AS CompletedOrders
    FROM orders o
    GROUP BY o.customer_id
),

-- Average customer review rating
ReviewMetrics AS (
    SELECT 
        customer_id,
        AVG(rating) AS AvgRating
    FROM reviews
    GROUP BY customer_id
),

-- Count of wishlist additions within last 60 days
WishlistMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistCount
    FROM wishlists
    WHERE added_date >= DATEADD(DAY, -60, '2025-05-07')
    GROUP BY customer_id
),

-- Count of successful payments per customer
PaymentMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS SuccessfulPayments
    FROM payments
    GROUP BY customer_id
),

-- Additional order-level aggregated stats
CustomerOrderStats AS (
    SELECT 
        o.customer_id,
        COUNT(*) AS TotalOrdersStats,
        COUNT(DISTINCT CAST(o.order_date AS DATE)) AS ActiveDays,
        SUM(o.total_amount) AS TotalSpent,
        AVG(o.total_amount) AS AvgOrderValue,
        COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 1.0 / COUNT(*) AS DeliveryRate,
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) * 1.0 / COUNT(*) AS CancelRate
    FROM orders o
    GROUP BY o.customer_id
),

-- Return statistics per customer
CustomerReturns AS (
    SELECT 
        o.customer_id,
        COUNT(r.id) AS TotalReturns,
        COUNT(r.id) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0) AS ReturnRate
    FROM orders o
    LEFT JOIN returns r ON o.id = r.order_id
    GROUP BY o.customer_id
),

-- Total wishlist items per customer (all time)
CustomerWishlists AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistItems
    FROM wishlists
    GROUP BY customer_id
),

-- Customer session counts and average duration
CustomerSessions AS (
    SELECT 
        customer_id,
        COUNT(*) AS SessionCount,
        AVG(DATEDIFF(MINUTE, session_start, session_end)) AS AvgSessionDuration
    FROM customer_sessions
    GROUP BY customer_id
),

-- Customer tenure in days
CustomerBase AS (
    SELECT
        c.id AS customer_id,
        DATEDIFF(DAY, c.registration_date, '2025-05-07') AS CustomerTenure
    FROM customers c
)

SELECT
    cb.customer_id,

    -- Core metrics
    cm.TotalOrders,
    cm.ActiveDaysRange AS ActiveDays,
    cm.ActiveMonths,
    cm.OrdersPerMonth,
    cm.DaysSinceLastOrder,
    CAST(cm.CompletedOrders AS FLOAT) / NULLIF(cm.TotalOrders, 0) AS OrderCompletionRate,

    -- Review metrics
    COALESCE(rm.AvgRating, 0) AS AvgRating,

    -- Wishlist metrics
    COALESCE(wm.WishlistCount, 0) AS WishlistCount,
    COALESCE(cw.WishlistItems, 0) AS WishlistItems,

    -- Payment metrics
    COALESCE(pm.SuccessfulPayments, 0) AS SuccessfulPayments,

    -- Order stats
    co.TotalSpent,
    co.AvgOrderValue,
    co.DeliveryRate,
    co.CancelRate,
    co.ActiveDays,

    -- Returns
    cr.TotalReturns,
    cr.ReturnRate,

    -- Sessions
    cs.SessionCount,
    cs.AvgSessionDuration,

    -- Base
    cb.CustomerTenure

FROM CustomerBase cb
LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id;


"""




# After applying equation of avg entropy-variance for target
query_test_gui = """

WITH 
-- Aggregate core customer order metrics
CustomerMetrics AS (
    SELECT 
        o.customer_id,
        COUNT(o.id) AS TotalOrders,
        DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS ActiveDaysRange,
        CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0 AS ActiveMonths,
        COUNT(o.id) / NULLIF(CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0, 0) AS OrdersPerMonth,
        DATEDIFF(DAY, MAX(o.order_date), '2025-05-07') AS DaysSinceLastOrder,
        SUM(CASE WHEN o.status IN ('delivered', 'shipped') THEN 1 ELSE 0 END) AS CompletedOrders
    FROM orders o
    GROUP BY o.customer_id
),

-- Average customer review rating
ReviewMetrics AS (
    SELECT 
        customer_id,
        AVG(rating) AS AvgRating
    FROM reviews
    GROUP BY customer_id
),

-- Count of wishlist additions within last 60 days
WishlistMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistCount
    FROM wishlists
    WHERE added_date >= DATEADD(DAY, -60, '2025-05-07')
    GROUP BY customer_id
),

-- Count of successful payments per customer
PaymentMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS SuccessfulPayments
    FROM payments
    GROUP BY customer_id
),

-- Additional order-level aggregated stats
CustomerOrderStats AS (
    SELECT 
        o.customer_id,
        COUNT(*) AS TotalOrdersStats,
        COUNT(DISTINCT CAST(o.order_date AS DATE)) AS ActiveDays,
        SUM(o.total_amount) AS TotalSpent,
        AVG(o.total_amount) AS AvgOrderValue,
        COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 1.0 / COUNT(*) AS DeliveryRate,
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) * 1.0 / COUNT(*) AS CancelRate
    FROM orders o
    GROUP BY o.customer_id
),

-- Return statistics per customer
CustomerReturns AS (
    SELECT 
        o.customer_id,
        COUNT(r.id) AS TotalReturns,
        COUNT(r.id) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0) AS ReturnRate
    FROM orders o
    LEFT JOIN returns r ON o.id = r.order_id
    GROUP BY o.customer_id
),

-- Total wishlist items per customer (all time)
CustomerWishlists AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistItems
    FROM wishlists
    GROUP BY customer_id
),

-- Customer session counts and average duration
CustomerSessions AS (
    SELECT 
        customer_id,
        COUNT(*) AS SessionCount,
        AVG(DATEDIFF(MINUTE, session_start, session_end)) AS AvgSessionDuration
    FROM customer_sessions
    GROUP BY customer_id
),

-- Customer tenure in days
CustomerBase AS (
    SELECT
        c.id AS customer_id,
        DATEDIFF(DAY, c.registration_date, '2025-05-07') AS CustomerTenure
    FROM customers c
),

-- Merge some features for scoring calculations
AllFeatures AS (
    SELECT 
        cb.customer_id,
        ISNULL(co.ActiveDays, 0) AS ActiveDays,
        cb.CustomerTenure,
        ISNULL(cs.SessionCount, 0) AS SessionCount,
        ISNULL(cw.WishlistItems, 0) AS WishlistItems,
        ISNULL(co.TotalSpent, 0) AS TotalSpent,
        ISNULL(cm.TotalOrders, 0) AS TotalOrders,
        ISNULL(cm.OrdersPerMonth, 0) AS OrdersPerMonth,
        ISNULL(pm.SuccessfulPayments, 0) AS SuccessfulPayments,
        ISNULL(wm.WishlistCount, 0) AS WishlistCount,
        COALESCE(rm.AvgRating, 0) AS AvgRating,
        ISNULL(cr.TotalReturns, 0) AS TotalReturns,
        ISNULL(cr.ReturnRate, 0) AS ReturnRate,
        ISNULL(cm.ActiveMonths, 0) AS ActiveMonths,
        CAST(cm.CompletedOrders AS FLOAT) / NULLIF(cm.TotalOrders, 0) AS OrderCompletionRate,
        ISNULL(co.AvgOrderValue, 0) AS AvgOrderValue,
        ISNULL(co.DeliveryRate, 0) AS DeliveryRate,
        ISNULL(cs.AvgSessionDuration, 0) AS AvgSessionDuration,
        ISNULL(co.CancelRate, 0) AS CancelRate,
        ISNULL(cm.DaysSinceLastOrder, 0) AS DaysSinceLastOrder
    FROM CustomerBase cb
    LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
    LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
    LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
    LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
    LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
    LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
    LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
    LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id
),

-- Score calculation
ScoredCustomers AS (
    SELECT *,
        (
            0.087922 * CustomerTenure +
            0.079801 * SessionCount +
            0.074038 * WishlistItems +
            0.069560 * TotalSpent +
            0.068929 * ActiveDays +
            0.068480 * TotalOrders +
            0.062416 * OrdersPerMonth +
            0.061116 * SuccessfulPayments +
            0.056173 * WishlistCount +
            0.046111 * AvgRating +
            0.043037 * TotalReturns +
            0.041851 * ActiveMonths +
            0.038045 * OrderCompletionRate +
            0.034751 * AvgOrderValue +
            0.032422 * DeliveryRate +
            0.032026 * AvgSessionDuration +
            0.029114 * CancelRate +
            0.027397 * DaysSinceLastOrder
        ) AS RawCustomerScore
    FROM AllFeatures
),

-- Get min and max for normalization
ScoreStats AS (
    SELECT 
        MIN(RawCustomerScore) AS MinScore,
        MAX(RawCustomerScore) AS MaxScore
    FROM ScoredCustomers
)

-- Final output with normalized CustomerScore and ordered columns
SELECT 
    cb.customer_id,

    -- Core features
    ISNULL(cm.TotalOrders, 0) AS TotalOrders,
    ISNULL(cm.ActiveMonths, 0) AS ActiveMonths,
    ISNULL(cm.OrdersPerMonth, 0) AS OrdersPerMonth,
    ISNULL(cm.DaysSinceLastOrder, 0) AS DaysSinceLastOrder,
    CASE WHEN ISNULL(cm.TotalOrders, 0) = 0 THEN 0 
         ELSE CAST(ISNULL(cm.CompletedOrders, 0) AS FLOAT) / cm.TotalOrders 
    END AS OrderCompletionRate,
    COALESCE(rm.AvgRating, 0) AS AvgRating,
    COALESCE(wm.WishlistCount, 0) AS WishlistCount,
    COALESCE(pm.SuccessfulPayments, 0) AS SuccessfulPayments,

    -- Extended features
    ISNULL(co.TotalSpent, 0) AS TotalSpent,
    ISNULL(co.AvgOrderValue, 0) AS AvgOrderValue,
    ISNULL(co.DeliveryRate, 0) AS DeliveryRate,
    ISNULL(co.CancelRate, 0) AS CancelRate,
    ISNULL(co.ActiveDays, 0) AS ActiveDays,
    ISNULL(cr.TotalReturns, 0) AS TotalReturns,
    ISNULL(cr.ReturnRate, 0) AS ReturnRate,
    ISNULL(cw.WishlistItems, 0) AS WishlistItems,
    ISNULL(cs.SessionCount, 0) AS SessionCount,
    ISNULL(cs.AvgSessionDuration, 0) AS AvgSessionDuration,
    cb.CustomerTenure,

    -- CustomerScore
    (sc.RawCustomerScore - ss.MinScore) / NULLIF((ss.MaxScore - ss.MinScore), 0) AS CustomerScore

FROM CustomerBase cb
LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id
INNER JOIN ScoredCustomers sc ON cb.customer_id = sc.customer_id
CROSS JOIN ScoreStats ss
WHERE cb.customer_id = '{customer_id}';


"""


query_test = """

WITH 
-- Aggregate core customer order metrics
CustomerMetrics AS (
    SELECT 
        o.customer_id,
        COUNT(o.id) AS TotalOrders,
        DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS ActiveDaysRange,
        CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0 AS ActiveMonths,
        COUNT(o.id) / NULLIF(CAST(DATEDIFF(DAY, MIN(o.order_date), MAX(o.order_date)) AS FLOAT) / 30.0, 0) AS OrdersPerMonth,
        DATEDIFF(DAY, MAX(o.order_date), '2025-05-07') AS DaysSinceLastOrder,
        SUM(CASE WHEN o.status IN ('delivered', 'shipped') THEN 1 ELSE 0 END) AS CompletedOrders
    FROM orders o
    GROUP BY o.customer_id
),

-- Average customer review rating
ReviewMetrics AS (
    SELECT 
        customer_id,
        AVG(rating) AS AvgRating
    FROM reviews
    GROUP BY customer_id
),

-- Count of wishlist additions within last 60 days
WishlistMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistCount
    FROM wishlists
    WHERE added_date >= DATEADD(DAY, -60, '2025-05-07')
    GROUP BY customer_id
),

-- Count of successful payments per customer
PaymentMetrics AS (
    SELECT 
        customer_id,
        COUNT(*) AS SuccessfulPayments
    FROM payments
    GROUP BY customer_id
),

-- Additional order-level aggregated stats
CustomerOrderStats AS (
    SELECT 
        o.customer_id,
        COUNT(*) AS TotalOrdersStats,
        COUNT(DISTINCT CAST(o.order_date AS DATE)) AS ActiveDays,
        SUM(o.total_amount) AS TotalSpent,
        AVG(o.total_amount) AS AvgOrderValue,
        COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 1.0 / COUNT(*) AS DeliveryRate,
        COUNT(CASE WHEN o.status = 'cancelled' THEN 1 END) * 1.0 / COUNT(*) AS CancelRate
    FROM orders o
    GROUP BY o.customer_id
),

-- Return statistics per customer
CustomerReturns AS (
    SELECT 
        o.customer_id,
        COUNT(r.id) AS TotalReturns,
        COUNT(r.id) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0) AS ReturnRate
    FROM orders o
    LEFT JOIN returns r ON o.id = r.order_id
    GROUP BY o.customer_id
),

-- Total wishlist items per customer (all time)
CustomerWishlists AS (
    SELECT 
        customer_id,
        COUNT(*) AS WishlistItems
    FROM wishlists
    GROUP BY customer_id
),

-- Customer session counts and average duration
CustomerSessions AS (
    SELECT 
        customer_id,
        COUNT(*) AS SessionCount,
        AVG(DATEDIFF(MINUTE, session_start, session_end)) AS AvgSessionDuration
    FROM customer_sessions
    GROUP BY customer_id
),

-- Customer tenure in days
CustomerBase AS (
    SELECT
        c.id AS customer_id,
        DATEDIFF(DAY, c.registration_date, '2025-05-07') AS CustomerTenure
    FROM customers c
),

-- Merge some features for scoring calculations
AllFeatures AS (
    SELECT 
        cb.customer_id,
        ISNULL(co.ActiveDays, 0) AS ActiveDays,
        cb.CustomerTenure,
        ISNULL(cs.SessionCount, 0) AS SessionCount,
        ISNULL(cw.WishlistItems, 0) AS WishlistItems,
        ISNULL(co.TotalSpent, 0) AS TotalSpent,
        ISNULL(cm.TotalOrders, 0) AS TotalOrders,
        ISNULL(cm.OrdersPerMonth, 0) AS OrdersPerMonth,
        ISNULL(pm.SuccessfulPayments, 0) AS SuccessfulPayments,
        ISNULL(wm.WishlistCount, 0) AS WishlistCount,
        COALESCE(rm.AvgRating, 0) AS AvgRating,
        ISNULL(cr.TotalReturns, 0) AS TotalReturns,
        ISNULL(cr.ReturnRate, 0) AS ReturnRate,
        ISNULL(cm.ActiveMonths, 0) AS ActiveMonths,
        CAST(cm.CompletedOrders AS FLOAT) / NULLIF(cm.TotalOrders, 0) AS OrderCompletionRate,
        ISNULL(co.AvgOrderValue, 0) AS AvgOrderValue,
        ISNULL(co.DeliveryRate, 0) AS DeliveryRate,
        ISNULL(cs.AvgSessionDuration, 0) AS AvgSessionDuration,
        ISNULL(co.CancelRate, 0) AS CancelRate,
        ISNULL(cm.DaysSinceLastOrder, 0) AS DaysSinceLastOrder
    FROM CustomerBase cb
    LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
    LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
    LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
    LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
    LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
    LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
    LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
    LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id
),

-- Score calculation
ScoredCustomers AS (
    SELECT *,
        (
            0.087922 * CustomerTenure +
            0.079801 * SessionCount +
            0.074038 * WishlistItems +
            0.069560 * TotalSpent +
            0.068929 * ActiveDays +
            0.068480 * TotalOrders +
            0.062416 * OrdersPerMonth +
            0.061116 * SuccessfulPayments +
            0.056173 * WishlistCount +
            0.046111 * AvgRating +
            0.043037 * TotalReturns +
            0.041851 * ActiveMonths +
            0.038045 * OrderCompletionRate +
            0.034751 * AvgOrderValue +
            0.032422 * DeliveryRate +
            0.032026 * AvgSessionDuration +
            0.029114 * CancelRate +
            0.027397 * DaysSinceLastOrder
        ) AS RawCustomerScore
    FROM AllFeatures
),

-- Get min and max for normalization
ScoreStats AS (
    SELECT 
        MIN(RawCustomerScore) AS MinScore,
        MAX(RawCustomerScore) AS MaxScore
    FROM ScoredCustomers
)

-- Final output with normalized CustomerScore and ordered columns
SELECT 
    cb.customer_id,

    -- Core features
    ISNULL(cm.TotalOrders, 0) AS TotalOrders,
    ISNULL(cm.ActiveMonths, 0) AS ActiveMonths,
    ISNULL(cm.OrdersPerMonth, 0) AS OrdersPerMonth,
    ISNULL(cm.DaysSinceLastOrder, 0) AS DaysSinceLastOrder,
    CASE WHEN ISNULL(cm.TotalOrders, 0) = 0 THEN 0 
         ELSE CAST(ISNULL(cm.CompletedOrders, 0) AS FLOAT) / cm.TotalOrders 
    END AS OrderCompletionRate,
    COALESCE(rm.AvgRating, 0) AS AvgRating,
    COALESCE(wm.WishlistCount, 0) AS WishlistCount,
    COALESCE(pm.SuccessfulPayments, 0) AS SuccessfulPayments,

    -- Extended features
    ISNULL(co.TotalSpent, 0) AS TotalSpent,
    ISNULL(co.AvgOrderValue, 0) AS AvgOrderValue,
    ISNULL(co.DeliveryRate, 0) AS DeliveryRate,
    ISNULL(co.CancelRate, 0) AS CancelRate,
    ISNULL(co.ActiveDays, 0) AS ActiveDays,
    ISNULL(cr.TotalReturns, 0) AS TotalReturns,
    ISNULL(cr.ReturnRate, 0) AS ReturnRate,
    ISNULL(cw.WishlistItems, 0) AS WishlistItems,
    ISNULL(cs.SessionCount, 0) AS SessionCount,
    ISNULL(cs.AvgSessionDuration, 0) AS AvgSessionDuration,
    cb.CustomerTenure,

    -- CustomerScore
    (sc.RawCustomerScore - ss.MinScore) / NULLIF((ss.MaxScore - ss.MinScore), 0) AS CustomerScore

FROM CustomerBase cb
LEFT JOIN CustomerMetrics cm ON cb.customer_id = cm.customer_id
LEFT JOIN ReviewMetrics rm ON cb.customer_id = rm.customer_id
LEFT JOIN WishlistMetrics wm ON cb.customer_id = wm.customer_id
LEFT JOIN PaymentMetrics pm ON cb.customer_id = pm.customer_id
LEFT JOIN CustomerOrderStats co ON cb.customer_id = co.customer_id
LEFT JOIN CustomerReturns cr ON cb.customer_id = cr.customer_id
LEFT JOIN CustomerWishlists cw ON cb.customer_id = cw.customer_id
LEFT JOIN CustomerSessions cs ON cb.customer_id = cs.customer_id
INNER JOIN ScoredCustomers sc ON cb.customer_id = sc.customer_id
CROSS JOIN ScoreStats ss;

"""