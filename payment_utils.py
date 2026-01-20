#!/usr/bin/env python3
"""
Payment utilities for Skileez learning marketplace
Handles Stripe payment processing, webhooks, and transfers
"""

import os
import logging
import stripe
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Tuple
from app import app, db
from models import Contract, SessionPayment, User
from notification_utils import create_contract_notification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Platform fee percentage (15%)
PLATFORM_FEE_PERCENTAGE = 0.15

class PaymentError(Exception):
    """Custom exception for payment-related errors"""
    pass

def get_stripe_client():
    """Get Stripe client with proper error handling"""
    if not stripe.api_key:
        raise PaymentError("Stripe secret key not configured")
    return stripe

def calculate_platform_fee(amount: float) -> float:
    """Calculate platform fee (15%)"""
    return amount * PLATFORM_FEE_PERCENTAGE

def calculate_coach_payout(amount: float) -> float:
    """Calculate coach payout after platform fee"""
    return amount - calculate_platform_fee(amount)

def create_payment_intent(contract_id: int, amount: float, currency: str = 'usd') -> Dict:
    """
    Create a Stripe PaymentIntent for contract payment
    
    Args:
        contract_id: ID of the contract being paid for
        amount: Payment amount in dollars
        currency: Currency code (default: 'usd')
    
    Returns:
        Dict containing payment intent data
    """
    try:
        with app.app_context():
            # Get contract details
            contract = Contract.query.get_or_404(contract_id)
            
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'contract_id': str(contract_id),
                    'student_id': str(contract.student_id),
                    'coach_id': str(contract.coach_id),
                    'contract_number': contract.contract_number
                },
                description=f"Payment for contract {contract.contract_number}",
                receipt_email=contract.student.email,
                application_fee_amount=int(calculate_platform_fee(amount) * 100),
                transfer_data={
                    'destination': get_coach_stripe_account(contract.coach_id),
                }
            )
            
            logger.info(f"Created payment intent {payment_intent.id} for contract {contract_id}")
            return {
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount,
                'currency': currency
            }
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {e}")
        raise PaymentError(f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise PaymentError(f"Payment setup error: {str(e)}")

def create_session_payment_intent(session_id: int, amount: float, currency: str = 'usd') -> Dict:
    """
    Create a Stripe PaymentIntent for individual session payment
    
    Args:
        session_id: ID of the session being paid for
        amount: Payment amount in dollars
        currency: Currency code (default: 'usd')
    
    Returns:
        Dict containing payment intent data
    """
    try:
        with app.app_context():
            # Get session and contract details
            from models import Session
            session = Session.query.get_or_404(session_id)
            contract = session.get_contract()
            
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'session_id': str(session_id),
                    'contract_id': str(contract.id),
                    'student_id': str(contract.student_id),
                    'coach_id': str(contract.coach_id)
                },
                description=f"Payment for session {session.session_number} of contract {contract.contract_number}",
                receipt_email=contract.student.email,
                application_fee_amount=int(calculate_platform_fee(amount) * 100),
                transfer_data={
                    'destination': get_coach_stripe_account(contract.coach_id),
                }
            )
            
            logger.info(f"Created session payment intent {payment_intent.id} for session {session_id}")
            return {
                'payment_intent_id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount,
                'currency': currency
            }
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating session payment intent: {e}")
        raise PaymentError(f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating session payment intent: {e}")
        raise PaymentError(f"Payment setup error: {str(e)}")

def get_coach_stripe_account(coach_id: int) -> str:
    """
    Get or create Stripe Connect account for coach
    
    Args:
        coach_id: ID of the coach
    
    Returns:
        Stripe account ID for the coach
    """
    try:
        with app.app_context():
            coach = User.query.get_or_404(coach_id)
            
            # Check if coach already has Stripe account
            if hasattr(coach, 'stripe_account_id') and coach.stripe_account_id:
                return coach.stripe_account_id
            
            # Create new Stripe Connect account
            account = stripe.Account.create(
                type='express',
                country='US',  # You can make this dynamic based on coach location
                email=coach.email,
                capabilities={
                    'card_payments': {'requested': True},
                    'transfers': {'requested': True},
                },
                business_type='individual',
                business_profile={
                    'url': 'https://skileez.com',
                    'mcc': '8299',  # Educational Services
                }
            )
            
            # Store Stripe account ID in coach profile
            if hasattr(coach, 'coach_profile'):
                coach.coach_profile.stripe_account_id = account.id
                db.session.commit()
            
            logger.info(f"Created Stripe account {account.id} for coach {coach_id}")
            return account.id
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating coach account: {e}")
        raise PaymentError(f"Coach account setup error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating coach account: {e}")
        raise PaymentError(f"Coach account error: {str(e)}")

def process_payment_webhook(event_data: Dict) -> bool:
    """
    Process Stripe webhook events
    
    Args:
        event_data: Stripe webhook event data
    
    Returns:
        True if processed successfully, False otherwise
    """
    try:
        with app.app_context():
            event_type = event_data.get('type')
            
            if event_type == 'payment_intent.succeeded':
                return handle_payment_success(event_data['data']['object'])
            elif event_type == 'payment_intent.payment_failed':
                return handle_payment_failure(event_data['data']['object'])
            elif event_type == 'transfer.created':
                return handle_transfer_created(event_data['data']['object'])
            elif event_type == 'charge.refunded':
                return handle_refund_processed(event_data['data']['object'])
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return True
                
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return False

def handle_payment_success(payment_intent: Dict) -> bool:
    """Handle successful payment"""
    try:
        with app.app_context():
            payment_intent_id = payment_intent['id']
            contract_id = payment_intent['metadata'].get('contract_id')
            session_id = payment_intent['metadata'].get('session_id')
            
            if contract_id:
                # Contract payment
                contract = Contract.query.get(int(contract_id))
                if contract:
                    # Use the proper method to mark payment as paid
                    contract.mark_payment_paid(payment_intent_id)
                    
                    # Log the contract status after payment
                    logger.info(f"Contract {contract_id} payment status: {contract.payment_status}, contract status: {contract.status}")
                    
                    # Create session payment records
                    for session in contract.get_all_sessions():
                        session_payment = SessionPayment(
                            session_id=session.id,
                            contract_id=contract.id,
                            amount=contract.rate,
                            status='paid',
                            stripe_payment_intent_id=payment_intent_id,
                            paid_at=datetime.utcnow()
                        )
                        db.session.add(session_payment)
                    
                    db.session.commit()
                    
                    # Log final contract status after commit
                    logger.info(f"Contract {contract_id} final status after commit: payment_status={contract.payment_status}, status={contract.status}")
                    
                    # Create notification for coach about payment received
                    create_contract_notification(contract, 'payment_received')
                    
                    logger.info(f"Contract {contract_id} payment processed successfully")
                    return True
                    
            elif session_id:
                # Individual session payment
                session_payment = SessionPayment.query.filter_by(
                    stripe_payment_intent_id=payment_intent_id
                ).first()
                
                if session_payment:
                    session_payment.status = 'paid'
                    session_payment.paid_at = datetime.utcnow()
                    db.session.commit()
                    logger.info(f"Session payment {session_id} processed successfully")
                    return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        return False

def handle_payment_failure(payment_intent: Dict) -> bool:
    """Handle failed payment"""
    try:
        with app.app_context():
            payment_intent_id = payment_intent['id']
            
            # Update session payment status
            session_payment = SessionPayment.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if session_payment:
                session_payment.status = 'failed'
                db.session.commit()
                logger.info(f"Payment {payment_intent_id} marked as failed")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        return False

def handle_transfer_created(transfer: Dict) -> bool:
    """Handle transfer to coach"""
    try:
        with app.app_context():
            transfer_id = transfer['id']
            amount = transfer['amount'] / 100  # Convert from cents
            
            # Find corresponding session payment
            session_payment = SessionPayment.query.filter_by(
                stripe_transfer_id=transfer_id
            ).first()
            
            if session_payment:
                session_payment.stripe_transfer_id = transfer_id
                db.session.commit()
                logger.info(f"Transfer {transfer_id} recorded for session payment")
                return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error handling transfer: {e}")
        return False

def handle_refund_processed(charge: Dict) -> bool:
    """Handle refund processing"""
    try:
        with app.app_context():
            payment_intent_id = charge.get('payment_intent')
            
            if payment_intent_id:
                session_payment = SessionPayment.query.filter_by(
                    stripe_payment_intent_id=payment_intent_id
                ).first()
                
                if session_payment:
                    session_payment.status = 'refunded'
                    db.session.commit()
                    logger.info(f"Refund processed for payment {payment_intent_id}")
                    return True
            
            return False
            
    except Exception as e:
        logger.error(f"Error handling refund: {e}")
        return False

def create_refund(payment_intent_id: str, amount: Optional[float] = None) -> Dict:
    """
    Create a refund for a payment
    
    Args:
        payment_intent_id: Stripe payment intent ID
        amount: Amount to refund (if None, refunds full amount)
    
    Returns:
        Dict containing refund data
    """
    try:
        # Get payment intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Create refund
        refund_data = {
            'payment_intent': payment_intent_id
        }
        
        if amount:
            refund_data['amount'] = int(amount * 100)  # Convert to cents
        
        refund = stripe.Refund.create(**refund_data)
        
        logger.info(f"Created refund {refund.id} for payment {payment_intent_id}")
        return {
            'refund_id': refund.id,
            'amount': refund.amount / 100,
            'status': refund.status
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating refund: {e}")
        raise PaymentError(f"Refund error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating refund: {e}")
        raise PaymentError(f"Refund processing error: {str(e)}")

def get_payment_status(payment_intent_id: str) -> Dict:
    """
    Get payment status from Stripe
    
    Args:
        payment_intent_id: Stripe payment intent ID
    
    Returns:
        Dict containing payment status
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return {
            'status': payment_intent.status,
            'amount': payment_intent.amount / 100,
            'currency': payment_intent.currency,
            'created': payment_intent.created,
            'last_payment_error': payment_intent.last_payment_error
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting payment status: {e}")
        raise PaymentError(f"Payment status error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise PaymentError(f"Payment status error: {str(e)}")

def create_coach_payout(coach_id: int, amount: float, currency: str = 'usd') -> Dict:
    """
    Create a payout to coach's bank account
    
    Args:
        coach_id: ID of the coach
        amount: Payout amount
        currency: Currency code
    
    Returns:
        Dict containing payout data
    """
    try:
        with app.app_context():
            coach = User.query.get_or_404(coach_id)
            stripe_account_id = get_coach_stripe_account(coach_id)
            
            # Create payout
            payout = stripe.Payout.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                stripe_account=stripe_account_id
            )
            
            logger.info(f"Created payout {payout.id} for coach {coach_id}")
            return {
                'payout_id': payout.id,
                'amount': amount,
                'currency': currency,
                'status': payout.status
            }
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payout: {e}")
        raise PaymentError(f"Payout error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payout: {e}")
        raise PaymentError(f"Payout processing error: {str(e)}")

def get_coach_balance(coach_id: int) -> Dict:
    """
    Get coach's Stripe balance
    
    Args:
        coach_id: ID of the coach
    
    Returns:
        Dict containing balance information
    """
    try:
        with app.app_context():
            stripe_account_id = get_coach_stripe_account(coach_id)
            
            balance = stripe.Balance.retrieve(stripe_account=stripe_account_id)
            
            return {
                'available': [{'amount': b.amount / 100, 'currency': b.currency} for b in balance.available],
                'pending': [{'amount': b.amount / 100, 'currency': b.currency} for b in balance.pending],
                'instant_available': [{'amount': b.amount / 100, 'currency': b.currency} for b in balance.instant_available]
            }
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error getting balance: {e}")
        raise PaymentError(f"Balance error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        raise PaymentError(f"Balance error: {str(e)}")

def verify_webhook_signature(payload: bytes, signature: str, webhook_secret: str) -> bool:
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Raw webhook payload
        signature: Stripe signature header
        webhook_secret: Webhook secret from Stripe
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return True
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return False
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return False

def handle_contract_payment_success(payment_intent: Dict) -> bool:
    """Handle successful contract payment"""
    try:
        with app.app_context():
            from models import Message
            
            contract_id = payment_intent.get('metadata', {}).get('contract_id')
            if not contract_id:
                logger.error("No contract_id in payment intent metadata")
                return False
            
            contract = Contract.query.get(int(contract_id))
            if not contract:
                logger.error(f"Contract {contract_id} not found")
                return False
            
            # Mark contract as paid
            contract.mark_payment_paid(payment_intent['id'])
            
            # Send notification messages
            success_message_student = Message(
                sender_id=contract.coach_id,
                recipient_id=contract.student_id,
                content=f"✅ Payment received! Contract #{contract.contract_number} is now active. You can start scheduling sessions!",
                sender_role='coach',
                recipient_role='student'
            )
            
            success_message_coach = Message(
                sender_id=contract.student_id,
                recipient_id=contract.coach_id,
                content=f"💰 Payment received for Contract #{contract.contract_number}! The contract is now active and ready for sessions.",
                sender_role='student',
                recipient_role='coach'
            )
            
            db.session.add(success_message_student)
            db.session.add(success_message_coach)
            db.session.commit()
            
            logger.info(f"Contract {contract_id} payment processed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error processing contract payment: {e}")
        return False

def create_payment_intent(amount: int, currency: str = 'usd', metadata: Dict = None) -> Dict:
    """
    Create a Stripe PaymentIntent for contract payment
    
    Args:
        amount: Payment amount in cents
        currency: Currency code (default: 'usd')
        metadata: Additional metadata for the payment
    
    Returns:
        Stripe PaymentIntent object
    """
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=metadata or {},
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        logger.info(f"Created payment intent {payment_intent.id}")
        return payment_intent
        
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating payment intent: {e}")
        raise PaymentError(f"Payment processing error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating payment intent: {e}")
        raise PaymentError(f"Payment setup error: {str(e)}")
