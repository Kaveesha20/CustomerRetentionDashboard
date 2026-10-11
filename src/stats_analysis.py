# src/stats_analysis.py
# Job: deeper statistical analysis that SQL alone doesn't do well -
# correlation, cohort/retention, and a significance test.
# Reads from SQL Server (the same tables load_db.py created).

import pandas as pd
from scipy import stats
from load_db import get_engine

engine = get_engine()


def correlation_delivery_vs_review():
    """
    Question: does delivery time affect how customers rate their order?
    We join orders + reviews, compute delivery days, then correlate
    it with review_score.
    """
    query = """
    SELECT o.order_id,
           DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_days,
           r.review_score
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
    """
    df = pd.read_sql(query, engine)

    # .corr() gives the correlation coefficient between the two columns
    correlation = df["delivery_days"].corr(df["review_score"])
    print(f"Correlation (delivery_days vs review_score): {correlation:.3f}")
    # Negative value = longer delivery tends to go with lower review score.
    # Close to 0 = little to no linear relationship.
    return df, correlation


def cohort_retention():
    """
    Question: what % of customers come back and order again?
    Uses customer_unique_id (the real person), not customer_id
    (which is one-per-order) - this matters, as we noted earlier.
    """
    query = """
    SELECT c.customer_unique_id, o.order_id, o.order_purchase_timestamp
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    """
    df = pd.read_sql(query, engine)

    # Count how many distinct orders each real customer made
    orders_per_customer = df.groupby("customer_unique_id")["order_id"].nunique()

    total_customers = orders_per_customer.shape[0]
    repeat_customers = (orders_per_customer > 1).sum()
    retention_rate = repeat_customers / total_customers

    print(f"Total unique customers: {total_customers}")
    print(f"Repeat customers (2+ orders): {repeat_customers}")
    print(f"Retention rate: {retention_rate:.2%}")
    return orders_per_customer, retention_rate


def ab_test_payment_type():
    """
    Question: do credit card payers spend significantly more per order
    than boleto payers? This is the same t-test pattern from Level 3
    theory, applied to a real business comparison.
    """
    query = """
    SELECT payment_type, payment_value
    FROM payments
    WHERE payment_type IN ('credit_card', 'boleto')
    """
    df = pd.read_sql(query, engine)

    group_a = df[df["payment_type"] == "credit_card"]["payment_value"]
    group_b = df[df["payment_type"] == "boleto"]["payment_value"]

    # ttest_ind compares the means of two independent groups.
    # equal_var=False = Welch's t-test, safer when the two groups
    # might have different variances (we don't assume they're equal).
    t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)

    print(f"Credit card avg: {group_a.mean():.2f} (n={len(group_a)})")
    print(f"Boleto avg: {group_b.mean():.2f} (n={len(group_b)})")
    print(f"t-statistic: {t_stat:.3f}, p-value: {p_value:.5f}")

    if p_value < 0.05:
        print("Result: statistically significant difference (p < 0.05)")
    else:
        print("Result: no statistically significant difference")

    return t_stat, p_value


if __name__ == "__main__":
    print("=== Correlation: Delivery Time vs Review Score ===")
    correlation_delivery_vs_review()

    print("\n=== Cohort / Retention Analysis ===")
    cohort_retention()

    print("\n=== A/B Test: Credit Card vs Boleto Payment Value ===")
    ab_test_payment_type()