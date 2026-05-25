{{
    config(
        materialized='incremental',
        unique_key='product_id',
        incremental_strategy='merge'
    )
}}

SELECT DISTINCT
    product_id,
    product_name
FROM {{ source('bronze', 'customer_transactions') }}
ORDER BY product_id
