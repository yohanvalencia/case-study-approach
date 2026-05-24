SELECT DISTINCT
    product_id,
    product_name
FROM {{ ref('stg_customer_transactions') }}
ORDER BY product_id
