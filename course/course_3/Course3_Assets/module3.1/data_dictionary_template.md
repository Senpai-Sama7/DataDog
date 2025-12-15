# Data Dictionary Template

Fill the table below for each field. Example provided for guidance.

| Field | Table | Type | Allowed Nulls | Description | Example | Notes |
|---|---|---|---|---|---|---|
| customer_id | Customers | INTEGER | No | Surrogate key for customer | 42 | Unique, stable |

## Tables
- Customers: customer_id, first_name, last_name, email, region, signup_date
- Orders: order_id, customer_id, order_date, channel, status, region, order_total

## Provenance
- Synthetic dataset generated for education.
- License: CC BY 4.0