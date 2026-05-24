WITH base AS (
    SELECT
        transaction_id,
        customer_id,
        transaction_date,
        DATE_TRUNC('month', transaction_date)::DATE AS month,
        product_id,
        quantity,
        price,
        tax,
        price + tax AS total_amount
    FROM {{ ref('stg_customer_transactions') }}
)

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    month,
    product_id,
    quantity,
    price,
    tax,
    total_amount,
    SUM(total_amount) OVER (PARTITION BY month)       AS monthly_total_revenue,
    SUM(total_amount) OVER (PARTITION BY customer_id) AS customer_total_spend
FROM base
