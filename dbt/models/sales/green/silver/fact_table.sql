{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        incremental_strategy='merge'
    )
}}

WITH base AS (
    SELECT
        ct.transaction_id,
        ct.customer_id,
        ct.transaction_date,
        DATE_TRUNC('month', ct.transaction_date)::DATE AS month,
        ct.product_id,
        ct.quantity,
        ct.price,
        ct.tax,
        ct.price + ct.tax AS total_amount
    FROM {{ source('bronze', 'customer_transactions') }} ct
    INNER JOIN {{ ref('dim_table') }} d ON ct.product_id = d.product_id
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
