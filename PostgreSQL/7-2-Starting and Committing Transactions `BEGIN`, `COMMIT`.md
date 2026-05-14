# Starting and Committing Transactions: `BEGIN`, `COMMIT`

Transactions are fundamental to database management, ensuring data consistency and reliability. This lesson delves into the core concepts of transactions, specifically focusing on how to initiate and finalize them using the `BEGIN` and `COMMIT` commands in PostgreSQL. Understanding these commands is crucial for managing database operations in a robust and predictable manner.

## Understanding Transactions: ACID Properties Revisited

As a brief recap from the previous module, transactions guarantee that database operations occur in a reliable and predictable manner, adhering to the ACID properties:

- **Atomicity:** A transaction is an indivisible unit of work; either all operations within it succeed, or none do.
- **Consistency:** A transaction transforms the database from one valid state to another. It maintains data integrity by adhering to defined rules and constraints.
- **Isolation:** Transactions are isolated from each other, preventing interference and ensuring that concurrent transactions do not corrupt data.
- **Durability:** Once a transaction is committed, its changes are permanent and survive even system failures.

## Starting a Transaction: The `BEGIN` Command

The `BEGIN` command is used to initiate a transaction in PostgreSQL. It signals the start of a series of operations that should be treated as a single logical unit. Until a `COMMIT` or `ROLLBACK` command is issued, all changes made to the database will be part of this transaction and not permanently saved.

### Syntax

The basic syntax is straightforward:

```sql
BEGIN;
```

Optionally, you can specify the isolation level and access mode at the beginning of the transaction. We will discuss isolation levels in detail in a later lesson, but for now, consider that it determines the degree to which concurrent transactions are isolated from each other. The access mode defines whether the transaction is read-only or read-write.

```sql
BEGIN ISOLATION LEVEL level READ WRITE; -- Or READ ONLY
```

Where `level` can be `SERIALIZABLE`, `REPEATABLE READ`, or `READ COMMITTED`. If `ISOLATION LEVEL` and/or `READ WRITE` are not specified, the database's default isolation level and read/write mode will be used.

### Example

Let's consider a simplified banking scenario. We have a table named `accounts` with columns `account_id` and `balance`. We want to transfer `$100` from account `1` to account `2`.

```sql
-- Start a new transaction
BEGIN;

-- Subtract $100 from account 1
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;

-- Add $100 to account 2
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- Commit the transaction to save the changes
COMMIT;
```

In this example, the `BEGIN` command starts the transaction. The subsequent `UPDATE` statements modify the `accounts` table. However, these changes are not yet permanent. They are only made permanent when the `COMMIT` command is executed. If, for example, there were insufficient funds in account `1`, we would use the `ROLLBACK` command, to be discussed in the next lesson, to undo the changes.

## Implicit Transactions

In some PostgreSQL client tools and configurations, a transaction may be started implicitly. For example, `psql`, the PostgreSQL interactive terminal, often operates in autocommit mode by default. In autocommit mode, each SQL statement is treated as a separate transaction and is automatically committed upon successful execution.

You can disable autocommit using the command:

```sql
SET AUTOCOMMIT OFF;
```

When autocommit is off, you must explicitly use `BEGIN` and `COMMIT`, or `ROLLBACK`, to manage transactions.

## Committing a Transaction: The `COMMIT` Command

The `COMMIT` command finalizes a transaction, making all changes permanent in the database. Once a transaction is committed, the changes are guaranteed to be durable, meaning they will survive system crashes or other failures.

### Syntax

The syntax for committing a transaction is simple:

```sql
COMMIT;
```

### Example

Continuing with the banking scenario, after performing the transfer, we use `COMMIT` to save the changes:

```sql
-- Start a new transaction
BEGIN;

-- Subtract $100 from account 1
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;

-- Add $100 to account 2
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- Commit the transaction to save the changes
COMMIT;
```

If the `COMMIT` command is successful, both `UPDATE` operations are permanently applied to the `accounts` table.

## The Importance of `COMMIT`

Without a `COMMIT` command, any changes made within a transaction are only visible to the current session and are not saved permanently. This ensures that if any part of the transaction fails, the entire transaction can be rolled back, maintaining data consistency.

## Practical Example: E-commerce Order Processing

Consider an e-commerce application where a customer places an order. The following operations need to occur within a single transaction:

1. Update the `products` table to reduce the quantity of the ordered items.
2. Create a new record in the `orders` table with the order details.
3. Create records in the `order_items` table for each item in the order.
4. Update the `customer_accounts` table to reflect the payment.

```sql
BEGIN;

-- Update product quantities
UPDATE products SET quantity = quantity - 2 WHERE product_id = 101;
UPDATE products SET quantity = quantity - 1 WHERE product_id = 102;

-- Insert order details
INSERT INTO orders (customer_id, order_date, total_amount)
VALUES (123, NOW(), 199.98);

-- Get the order ID of the recently placed order
-- Note: this example uses a simplified approach for illustration purposes.
-- In a real-world scenario, you would retrieve the newly generated order ID
-- using appropriate database-specific functions, such as the RETURNING clause
-- in PostgreSQL.
SELECT currval(pg_get_serial_sequence('orders', 'order_id')) INTO order_id;

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (order_id, 101, 2, 79.99);

INSERT INTO order_items (order_id, product_id, quantity, price)
VALUES (order_id, 102, 1, 39.99);

-- Update customer account
UPDATE customer_accounts SET balance = balance - 199.98 WHERE customer_id = 123;

COMMIT;
```

If any of these operations fail, such as insufficient stock or payment failure, the entire transaction should be rolled back using `ROLLBACK` to prevent data inconsistencies.

## Hypothetical Scenario: University Enrollment System

Imagine a university enrollment system where students register for courses. A transaction would encompass the following steps:

1. Check if the student meets the prerequisites for the course.
2. Verify if there are available seats in the course.
3. Update the student's record to include the course.
4. Update the course's record to reflect the new enrollment.

```sql
BEGIN;

-- Check prerequisites (simplified)
SELECT has_prerequisites FROM students WHERE student_id = 'S123';

-- Check available seats (simplified)
SELECT seats_available FROM courses WHERE course_id = 'CS101';

-- Update student record
INSERT INTO student_courses (student_id, course_id) VALUES ('S123', 'CS101');

-- Update course record
UPDATE courses SET seats_available = seats_available - 1 WHERE course_id = 'CS101';

COMMIT;
```

If any of these checks fail, such as the student not meeting the prerequisites or the course being full, the transaction should be rolled back to maintain the integrity of the enrollment data.

## Exercises

1. **Simulate a bank transfer:** Create a table `accounts` with columns `account_id` (`INT`, `PRIMARY KEY`) and `balance` (`DECIMAL`). Populate it with a few sample accounts. Write a transaction to transfer an amount from one account to another. Ensure that the transaction handles the case where the source account has insufficient funds. You do not need to implement rollback logic yet; just consider how you would check for it.

2. **E-commerce order:** Expand the e-commerce example. Include a check to verify that the customer has enough balance in their account before processing the order.

3. **University Course Registration:** Create `students` and `courses` tables. Add `student_id`, `course_id`, and other relevant columns such as `has_prerequisites` (`boolean`) to the `students` table, and `seats_available` to the `courses` table. Attempt to enroll a student in a course, making sure to check prerequisites and seat availability before committing the changes.

## Preparing for Future Lessons

This lesson laid the groundwork for understanding transactions by focusing on starting and committing them using `BEGIN` and `COMMIT`. In the next lesson, we will explore `ROLLBACK`, the command used to undo changes made within a transaction. We will also look at different scenarios and best practices for using `ROLLBACK` to handle errors and maintain data integrity. Furthermore, we will delve into more complex transaction management techniques.
