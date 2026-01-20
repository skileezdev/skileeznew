# PostgreSQL Database Recovery Guide

## Issue Description

You're encountering PostgreSQL transaction failures:

```
WARNING:__main__:⚠️ Could not add contract.stripe_payment_intent_id: (psycopg2.errors.InFailedSqlTransaction) current transaction is aborted, commands ignored until end of transaction block
```

This happens when a PostgreSQL transaction is in a failed state and all subsequent commands are ignored until the transaction is properly reset.

## Solutions (Try in Order)

### Solution 1: Run the Aggressive Recovery Script

```bash
python fix_postgresql_aggressive.py
```

This script:
- Completely resets the PostgreSQL connection
- Uses `ROLLBACK` and `RESET ALL` commands
- Creates fresh connections for each column addition
- Handles transaction failures automatically

### Solution 2: Run the Standard Recovery Script

```bash
python fix_postgresql_transaction.py
```

This script:
- Resets the database connection
- Adds columns with proper error handling
- Retries failed operations with fresh connections

### Solution 3: Manual SQL Execution

If the Python scripts don't work, run the SQL script directly in your PostgreSQL database:

1. **Connect to your PostgreSQL database** (using psql, pgAdmin, or your preferred client)

2. **Run the manual SQL script**:
   ```sql
   -- Copy and paste the contents of add_columns_manually.sql
   ```

3. **Or run individual commands**:
   ```sql
   -- Reset transaction state
   ROLLBACK;
   
   -- Add columns one by one
   ALTER TABLE coach_profile ADD COLUMN IF NOT EXISTS stripe_account_id VARCHAR(255);
   ALTER TABLE coach_profile ADD COLUMN IF NOT EXISTS stripe_account_status VARCHAR(50);
   ALTER TABLE contract ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(255);
   ALTER TABLE contract ADD COLUMN IF NOT EXISTS payment_date TIMESTAMP;
   ALTER TABLE session_payment ADD COLUMN IF NOT EXISTS stripe_transfer_id VARCHAR(255);
   ALTER TABLE session_payment ADD COLUMN IF NOT EXISTS transfer_date TIMESTAMP;
   ```

### Solution 4: Direct Database Connection Reset

If you have direct access to the PostgreSQL server:

1. **Connect to PostgreSQL as superuser**:
   ```bash
   psql -U postgres -d your_database_name
   ```

2. **Kill any stuck transactions**:
   ```sql
   -- List active connections
   SELECT pid, usename, application_name, state, query 
   FROM pg_stat_activity 
   WHERE state = 'active';
   
   -- Kill specific connection (replace PID with actual process ID)
   SELECT pg_terminate_backend(PID);
   ```

3. **Reset the database connection**:
   ```sql
   -- Reset all session variables
   RESET ALL;
   
   -- Commit any pending transactions
   COMMIT;
   ```

### Solution 5: Application-Level Reset

If you're running this in a web application:

1. **Restart your application server** (Flask, Django, etc.)
2. **Clear any connection pools**
3. **Re-run the deployment script**

## Prevention Strategies

### 1. **Use Transaction Management**
```python
from contextlib import contextmanager

@contextmanager
def safe_transaction(db_session):
    try:
        yield db_session
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
```

### 2. **Implement Retry Logic**
```python
def add_column_with_retry(table_name, column_name, column_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            db.session.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            db.session.commit()
            return True
        except Exception as e:
            if "InFailedSqlTransaction" in str(e):
                db.session.rollback()
                db.session.close()
                db.engine.dispose()
                time.sleep(1)
                continue
            else:
                raise e
    return False
```

### 3. **Use Connection Pooling**
```python
# In your Flask app configuration
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}
```

## Verification

After running any solution, verify the columns were added:

```sql
-- Check if columns exist
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name IN ('coach_profile', 'contract', 'session_payment')
    AND column_name IN (
        'stripe_account_id', 'stripe_account_status',
        'stripe_payment_intent_id', 'payment_date',
        'stripe_transfer_id', 'transfer_date'
    )
ORDER BY table_name, column_name;
```

## Expected Output

After successful recovery, you should see:

```
✅ Column coach_profile.stripe_account_id exists
✅ Column coach_profile.stripe_account_status exists
✅ Column contract.stripe_payment_intent_id exists
✅ Column contract.payment_date exists
✅ Column session_payment.stripe_transfer_id exists
✅ Column session_payment.transfer_date exists
✅ All required columns exist
```

## Troubleshooting

### If scripts still fail:

1. **Check database permissions**:
   ```sql
   -- Verify your user has ALTER permissions
   SELECT has_table_privilege('your_username', 'coach_profile', 'ALTER');
   ```

2. **Check for locks**:
   ```sql
   -- Check for table locks
   SELECT * FROM pg_locks WHERE relation::regclass::text LIKE '%coach_profile%';
   ```

3. **Restart PostgreSQL service** (if you have server access):
   ```bash
   sudo systemctl restart postgresql
   ```

### If you're using Render.com:

1. **Check the deployment logs** for specific error messages
2. **Verify environment variables** are set correctly
3. **Try redeploying** with a fresh database connection

## Next Steps

Once the columns are successfully added:

1. **Run the deployment verification**:
   ```bash
   python deploy_simple.py
   ```

2. **Test the application** to ensure everything works correctly

3. **Monitor the logs** for any remaining issues

## Support

If none of these solutions work, please provide:
- Complete error logs
- Database connection details (without sensitive info)
- PostgreSQL version
- Application framework and version
