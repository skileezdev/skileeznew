# Payment Test Mode Documentation

## Overview

The Payment Test Mode is a development feature that allows you to bypass Stripe integration during development and testing. When enabled, the payment system will simulate successful payments without making any real charges.

## Features

### 🔧 Configuration
- **Environment Variable**: `TEST_MODE=true` or `TEST_MODE=false`
- **Admin Toggle**: Toggle test mode on/off from the admin dashboard
- **Session Persistence**: Test mode setting persists for the current session

### 🎯 Test Mode Indicators
- **Payment Form Banner**: Yellow warning banner when test mode is active
- **Test Payment Button**: Quick "Process Test Payment" button with pre-filled test data
- **Admin Dashboard**: Visual indicator and toggle switch in admin panel
- **Payment Records**: Test payments are marked with "TEST MODE" indicator

### 🚀 Functionality
- **Bypass Stripe**: No real payment processing occurs
- **Form Validation**: Basic validation still applies (card number, cardholder name)
- **Test Data**: Accepts any payment data for testing
- **Notifications**: Sends test payment notifications to users
- **Session Creation**: Creates real session records for contracts

## Setup Instructions

### 1. Environment Variable Setup

Add to your `.env` file or set as environment variable:

```bash
# Enable test mode
TEST_MODE=true

# Disable test mode (production)
TEST_MODE=false
```

### 2. Application Restart

After changing the environment variable, restart your Flask application:

```bash
# Stop the current application
# Then restart with new environment
python app.py
```

### 3. Admin Dashboard Toggle

1. Log in as an admin user
2. Navigate to the admin dashboard
3. Find the "Payment Test Mode" section
4. Toggle the switch to enable/disable test mode
5. Confirm the change

## Usage Guide

### For Developers

1. **Enable Test Mode**:
   ```bash
   export TEST_MODE=true
   python app.py
   ```

2. **Test Payment Flow**:
   - Log in as a student
   - Create or accept a contract
   - Navigate to payment page
   - Use the "Process Test Payment" button or fill form with any data
   - Verify payment completion and session creation

3. **Verify Test Mode**:
   - Check for yellow test mode banner
   - Look for test payment button
   - Verify form validation bypass
   - Check payment records for "TEST MODE" indicator

### For Testing

1. **Manual Testing**:
   ```bash
   python test_payment_mode.py
   ```

2. **Test Scenarios**:
   - Test with valid payment data
   - Test with invalid payment data
   - Test form validation bypass
   - Test admin toggle functionality
   - Test notification delivery

### For Production

1. **Disable Test Mode**:
   ```bash
   export TEST_MODE=false
   ```

2. **Verify Production Mode**:
   - No test mode banners
   - No test payment buttons
   - Full form validation active
   - Real Stripe integration (when implemented)

## File Changes

### Modified Files

1. **`app.py`**:
   - Added `TEST_MODE` configuration
   - Added `TEST_MODE_ENABLED` alias

2. **`templates/contracts/payment.html`**:
   - Added test mode banner
   - Added test payment button
   - Modified form validation to bypass in test mode
   - Added test data auto-fill functionality

3. **`routes.py`**:
   - Modified `contract_payment` route to handle test mode
   - Added test mode payment processing logic
   - Added `admin_toggle_test_mode` route

4. **`templates/admin/dashboard.html`**:
   - Added test mode toggle section
   - Added test mode status indicator
   - Added toggle functionality with JavaScript

### New Files

1. **`test_payment_mode.py`**:
   - Test script for verifying test mode functionality
   - Configuration checks
   - Manual testing instructions

2. **`PAYMENT_TEST_MODE.md`**:
   - This documentation file

## Security Considerations

### Test Mode Safety
- ✅ No real charges are made in test mode
- ✅ Test payments are clearly marked
- ✅ Admin-only toggle access
- ✅ Session-based persistence (resets on restart)

### Production Safety
- ✅ Test mode disabled by default
- ✅ Environment variable control
- ✅ Admin dashboard warnings
- ✅ Clear visual indicators

## Troubleshooting

### Common Issues

1. **Test Mode Not Working**:
   - Check environment variable is set correctly
   - Restart the application after changing environment
   - Verify admin toggle is enabled

2. **Test Payment Button Not Appearing**:
   - Ensure test mode is enabled
   - Check browser console for JavaScript errors
   - Verify template changes are applied

3. **Form Validation Still Active**:
   - Check JavaScript is loading correctly
   - Verify test mode variable is being passed to template
   - Clear browser cache

### Debug Steps

1. **Check Configuration**:
   ```python
   import os
   print(f"TEST_MODE: {os.environ.get('TEST_MODE')}")
   ```

2. **Check App Config**:
   ```python
   from app import app
   print(f"App TEST_MODE: {app.config.get('TEST_MODE')}")
   ```

3. **Check Template Variables**:
   - Inspect page source for test mode variable
   - Check browser console for JavaScript errors

## Future Enhancements

### Planned Features
- [ ] Test mode logging and analytics
- [ ] Test payment simulation delays
- [ ] Test mode expiration timers
- [ ] Test mode audit trails
- [ ] Test mode user notifications

### Integration Points
- [ ] Stripe webhook simulation
- [ ] Payment failure simulation
- [ ] Refund simulation
- [ ] Subscription payment simulation

## Support

For issues or questions about the payment test mode:

1. Check this documentation
2. Run the test script: `python test_payment_mode.py`
3. Review the configuration files
4. Check application logs for errors

---

**Note**: This test mode is for development and testing purposes only. Always ensure test mode is disabled in production environments.
