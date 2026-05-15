# Rolling Back Transactions: `ROLLBACK`

Transactions are crucial for maintaining data integrity in a database, especially when dealing with complex operations. They allow you to treat a series of database operations as a single logical unit of work. Either all operations within a transaction are successfully applied to the database, or none are. The `ROLLBACK` command is the mechanism to ensure the “none” part of this guarantee. It effectively undoes any changes made during the current transaction, restoring the database to its state before the transaction began.

This lesson delves into the specifics of using `ROLLBACK` in PostgreSQL.

## Understanding `ROLLBACK`

The `ROLLBACK` command in PostgreSQL is used to terminate the current transaction and undo all changes made since the transaction began. It is your safety net, allowing you to revert the database to a consistent state if errors occur or if you decide that the changes made during the transaction should not be permanently applied.

## Syntax

The basic syntax of the `ROLLBACK` command is straightforward:

```sql
ROLLBACK;
```

Optionally, you can roll back to a specific savepoint, which will be discussed later:

```sql
ROLLBACK TO savepoint_name;
```

## Principles of `ROLLBACK`

### Atomicity

`ROLLBACK` ensures the atomicity of a transaction. This means that a transaction is treated as a single, indivisible unit. Either all the changes within the transaction are applied if you `COMMIT`, or none are applied if you `ROLLBACK`.

### Data Consistency

By rolling back a transaction, you guarantee that the database remains in a consistent state. If an error occurs during a complex series of operations, `ROLLBACK` prevents partial updates from corrupting your data.

### Error Handling

`ROLLBACK` is a critical part of error handling in database applications. When an error is detected during a transaction, a `ROLLBACK` ensures that the database is not left in an inconsistent state.

## Practical Examples of `ROLLBACK`

Let’s illustrate the usage of `ROLLBACK` with examples based on a hypothetical online store database. Suppose we have:

- An `accounts` table to manage user balances
- A `products` table to manage product inventory

## Basic `ROLLBACK` Example: Insufficient Funds

Imagine a scenario where a customer attempts to purchase an item, but their account has insufficient funds. We can use `ROLLBACK` to revert the transaction.

### Start a Transaction

```sql
BEGIN;
```

### Check the Account Balance

```sql
SELECT balance FROM accounts WHERE account_id = 123;
```

Assume the query returns a balance of `$50`.

### Attempt to Deduct the Purchase Amount

Suppose the purchase amount is `$100`:

```sql
UPDATE accounts SET balance = balance - 100 WHERE account_id = 123;
```

### Check Whether the Balance Is Sufficient

```sql
SELECT balance FROM accounts WHERE account_id = 123;
```

Now, the balance is `-50`. This is not acceptable.

### Roll Back the Transaction

```sql
ROLLBACK;
```

After the `ROLLBACK`, the `accounts` table is restored to its original state before the transaction began. The customer’s balance remains `$50`.

## `ROLLBACK` with Multiple Operations: Order Processing

Consider a more complex scenario involving multiple operations, such as processing an order.

### Start a Transaction

```sql
BEGIN;
```

### Update the Customer’s Account

```sql
UPDATE accounts SET balance = balance - 50 WHERE account_id = 123;
```

### Update the Product Inventory

```sql
UPDATE products SET quantity = quantity - 1 WHERE product_id = 456;
```

### Insert a Record into the `orders` Table

```sql
INSERT INTO orders (account_id, product_id, quantity, order_date)
VALUES (123, 456, 1, NOW());
```

### Simulate an Error

```sql
-- Simulate an error, for example, a constraint violation
INSERT INTO shipping_queue (order_id) VALUES (NULL); -- Assuming order_id is NOT NULL
```

### Roll Back the Transaction

```sql
ROLLBACK;
```

Because of the error inserting into `shipping_queue`, the `ROLLBACK` command undoes all the previous operations within the transaction:

- The customer’s account balance remains unchanged.
- The product inventory is not updated.
- No record is inserted into the `orders` table.

## `ROLLBACK` to Savepoints

Savepoints allow you to roll back to a specific point within a transaction, rather than rolling back the entire transaction. This can be useful for handling errors in complex transactions where you only want to undo a portion of the changes.

### Start a Transaction

```sql
BEGIN;
```

### Update the Customer Account

```sql
UPDATE accounts SET balance = balance - 20 WHERE account_id = 123;
```

### Create a Savepoint

```sql
SAVEPOINT after_account_update;
```

### Update Product Inventory

```sql
UPDATE products SET quantity = quantity - 2 WHERE product_id = 456;
```

### Simulate an Error

```sql
-- Simulate an error
INSERT INTO delivery_schedule (order_id, delivery_date)
VALUES (999, 'Invalid Date'); -- Assuming date validation fails
```

### Roll Back to the Savepoint

```sql
ROLLBACK TO after_account_update;
```

In this case, only the following statements are rolled back:

- `UPDATE products`
- `INSERT INTO delivery_schedule`

The `UPDATE accounts` statement remains in effect. You can then correct the error, such as providing a valid date, and retry the inventory update and delivery schedule insertion. After correcting the error, you can then `COMMIT` the transaction.

## Advanced Example: Nested Transactions and `ROLLBACK`

While PostgreSQL does not support true nested transactions, you can simulate them using savepoints. This allows for finer-grained control over rollback behavior within a larger transaction.

### Start a Transaction

```sql
BEGIN;
```

### Perform Some Operations

```sql
UPDATE accounts SET balance = balance - 10 WHERE account_id = 123;
```

### Create a Savepoint for the “Nested” Transaction

```sql
SAVEPOINT nested_transaction;
```

### Perform Operations Within the “Nested” Transaction

```sql
UPDATE products SET quantity = quantity - 1 WHERE product_id = 789;
```

### Decide to Roll Back the “Nested” Transaction

```sql
ROLLBACK TO nested_transaction;
```

Only the product quantity update is rolled back. The account balance update remains.

### Continue with the Outer Transaction

```sql
UPDATE accounts SET balance = balance + 5 WHERE account_id = 456;
```

### Commit the Outer Transaction

```sql
COMMIT;
```

## Exercises

### 1. Account Transfer

Write a transaction that transfers money from one account to another. Include a check to ensure the source account has sufficient funds. If not, roll back the transaction.

### 2. Order Placement with Discount

Create a transaction that places an order, applies a discount if a coupon code is valid, and updates the customer’s loyalty points. Use a savepoint before applying the discount. If the discount application fails, such as because of an invalid coupon, roll back to the savepoint and continue with the order without the discount.

### 3. Inventory Adjustment

Imagine a scenario where you receive a shipment of new products. Write a transaction that updates the product inventory and records the shipment in a separate `shipments` table. If the shipment recording fails, roll back the entire inventory update.

## Summary

The `ROLLBACK` command is a fundamental tool for maintaining data integrity in PostgreSQL. It allows you to undo changes made during a transaction, ensuring that your database remains in a consistent state even when errors occur.

The use of savepoints provides even finer-grained control over rollback behavior, allowing you to selectively undo parts of a larger transaction. Understanding and using `ROLLBACK` is crucial for building robust and reliable database applications.

## Next Steps

Next, explore concurrency control mechanisms in PostgreSQL, including locking and isolation levels, which work in conjunction with transactions to manage concurrent access to data.
