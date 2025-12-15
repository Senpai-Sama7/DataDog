DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL,
  region TEXT NOT NULL,
  signup_date DATE NOT NULL
);

CREATE TABLE products (
  product_id INTEGER PRIMARY KEY,
  category TEXT NOT NULL,
  product_name TEXT NOT NULL,
  unit_cost REAL NOT NULL,
  unit_price REAL NOT NULL
);

CREATE TABLE orders (
  order_id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  order_date DATE NOT NULL,
  channel TEXT NOT NULL,
  status TEXT NOT NULL,
  region TEXT NOT NULL,
  order_total REAL NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
  order_item_id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  discount REAL NOT NULL,
  line_total REAL NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);