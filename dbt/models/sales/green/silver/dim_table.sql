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
{% if is_incremental() %}
WHERE product_id NOT IN (SELECT product_id FROM {{ this }})
{% endif %}
ORDER BY product_id
