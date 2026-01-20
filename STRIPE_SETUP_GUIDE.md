# Stripe Payment Integration Setup Guide

## Overview

This guide will help you set up Stripe payment integration for your Skileez learning marketplace. The integration includes:

- **Stripe Connect** for coach payouts
- **Payment Intents** for secure payments
- **Webhooks** for real-time payment updates
- **Refunds** and dispute handling
- **Platform fees** (15% like Upwork)

## Prerequisites

1. **Stripe Account**: Sign up at [stripe.com](https://stripe.com)
2. **Domain**: Your application must be accessible via HTTPS
3. **Environment Variables**: Configure the required keys

## Step 1: Stripe Dashboard Setup

### 1.1 Get Your API Keys

1. Log into your [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **API keys**
3. Copy your **Publishable key** and **Secret key**
4. For testing, use the test keys (start with `pk_test_` and `sk_test_`)

### 1.2 Enable Stripe Connect

1. Go to **Connect** → **Settings**
2. Enable **Express accounts** for coaches
3. Configure your business information
4. Set up your payout schedule

### 1.3 Configure Webhooks

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set the endpoint URL to: `https://yourdomain.com/webhooks/stripe`
4. Select these events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `transfer.created`
   - `charge.refunded`
5. Copy the **Webhook signing secret**

## Step 2: Environment Variables

Add these environment variables to your deployment:

### For Development (.env file)
```bash
STRIPE_SECRET_KEY=sk_test_your_test_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### For Production (Render)
```bash
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Step 3: Database Migration

Run the migration to add Stripe fields:

```bash
python deploy_migrate_simple.py
```

This will add:
- `stripe_customer_id` to the `user` table
- `stripe_account_id` to the `coach_profile` table

## Step 4: Testing the Integration

### 4.1 Test Payment Flow

1. **Create a test contract** in your application
2. **Initiate payment** using the payment form
3. **Use test card numbers**:
   - Success: `4242 4242 4242 4242`
   - Decline: `4000 0000 0000 0002`
   - 3D Secure: `4000 0025 0000 3155`

### 4.2 Test Webhooks

1. Use Stripe CLI for local testing:
   ```bash
   stripe listen --forward-to localhost:5000/webhooks/stripe
   ```

2. Or use the Stripe Dashboard to send test webhooks

## Step 5: Frontend Integration

### 5.1 Add Stripe.js

Include Stripe.js in your payment templates:

```html
<script src="https://js.stripe.com/v3/"></script>
```

### 5.2 Create Payment Form

```html
<form id="payment-form">
  <div id="card-element">
    <!-- Stripe Elements will create input elements here -->
  </div>
  <div id="card-errors" role="alert"></div>
  <button type="submit">Submit Payment</button>
</form>
```

### 5.3 JavaScript for Payment Processing

```javascript
// Initialize Stripe
const stripe = Stripe('pk_test_your_publishable_key');
const elements = stripe.elements();

// Create card element
const card = elements.create('card');
card.mount('#card-element');

// Handle form submission
const form = document.getElementById('payment-form');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const {paymentIntent, error} = await stripe.confirmCardPayment(
    clientSecret, {
      payment_method: {
        card: card,
        billing_details: {
          name: 'Student Name',
          email: 'student@example.com'
        }
      }
    }
  );
  
  if (error) {
    // Handle error
    console.error(error);
  } else {
    // Payment successful
    window.location.href = '/payment-success';
  }
});
```

## Step 6: Coach Onboarding

### 6.1 Stripe Connect Setup

When a coach signs up, they need to complete Stripe Connect onboarding:

1. **Create Express Account**: The system automatically creates a Stripe Connect account
2. **Onboarding Link**: Generate an onboarding link for the coach
3. **Bank Account**: Coach adds their bank account for payouts
4. **Verification**: Coach completes identity verification

### 6.2 Onboarding Flow

```python
from payment_utils import get_coach_stripe_account

def create_coach_onboarding_link(coach_id):
    stripe_account_id = get_coach_stripe_account(coach_id)
    
    account_link = stripe.AccountLink.create(
        account=stripe_account_id,
        refresh_url='https://yourdomain.com/coach/onboarding/refresh',
        return_url='https://yourdomain.com/coach/onboarding/complete',
        type='account_onboarding',
    )
    
    return account_link.url
```

## Step 7: Payment Processing Flow

### 7.1 Contract Payment

1. **Student accepts proposal** → Contract created
2. **Payment intent created** → Stripe generates payment intent
3. **Student pays** → Payment processed via Stripe
4. **Webhook received** → Payment status updated in database
5. **Funds transferred** → Coach receives payout (minus platform fee)

### 7.2 Session Payment

1. **Session completed** → Coach marks session as complete
2. **Payment intent created** → For individual session
3. **Student pays** → Payment processed
4. **Funds transferred** → Coach receives payout

## Step 8: Security Best Practices

### 8.1 Environment Variables

- ✅ Store keys in environment variables
- ❌ Never commit keys to version control
- ✅ Use different keys for test/production

### 8.2 Webhook Security

- ✅ Verify webhook signatures
- ✅ Use HTTPS endpoints
- ✅ Handle webhook failures gracefully

### 8.3 Data Protection

- ✅ Don't store sensitive card data
- ✅ Use Stripe's secure payment methods
- ✅ Implement proper error handling

## Step 9: Monitoring and Analytics

### 9.1 Stripe Dashboard

Monitor your payments in the Stripe Dashboard:
- **Payments**: View all transactions
- **Connect**: Monitor coach payouts
- **Webhooks**: Check webhook delivery
- **Disputes**: Handle chargebacks

### 9.2 Application Logs

The integration includes comprehensive logging:
- Payment processing events
- Webhook processing
- Error handling
- Coach onboarding

## Step 10: Going Live

### 10.1 Switch to Live Keys

1. Replace test keys with live keys
2. Update webhook endpoints
3. Test with small amounts first
4. Monitor transactions closely

### 10.2 Compliance

Ensure compliance with:
- **PCI DSS**: Stripe handles most requirements
- **GDPR**: Handle customer data properly
- **Local regulations**: Check your jurisdiction

## Troubleshooting

### Common Issues

1. **Webhook failures**: Check endpoint URL and signature verification
2. **Payment declines**: Review Stripe's decline codes
3. **Connect onboarding**: Ensure coach completes all steps
4. **Payout delays**: Check payout schedule and bank holidays

### Support Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)
- [Stripe Community](https://community.stripe.com)

## Testing Checklist

- [ ] Test payment success flow
- [ ] Test payment failure flow
- [ ] Test webhook processing
- [ ] Test coach onboarding
- [ ] Test refund processing
- [ ] Test dispute handling
- [ ] Test platform fee calculation
- [ ] Test payout transfers

## Security Checklist

- [ ] Environment variables configured
- [ ] Webhook signatures verified
- [ ] HTTPS endpoints used
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Test keys used in development
- [ ] Live keys secured in production

Your Stripe integration is now ready to process payments securely! 🎉
