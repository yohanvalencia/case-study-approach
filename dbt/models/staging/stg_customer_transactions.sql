SELECT
    transaction_id,
    customer_id,
    transaction_date,
    product_id,
    product_name,
    quantity,
    price,
    tax
FROM {{ source('bronze', 'customer_transactions') }}
