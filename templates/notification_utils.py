from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_contract_notification(contract, notification_type, recipient_id=None):
    """
    Create notifications for contract-related events
    
    Args:
        contract: Contract object
        notification_type: Type of notification ('sent', 'accepted', 'rejected', 'payment_received', etc.)
        recipient_id: Optional specific recipient ID (if None, uses contract parties)
    """
    try:
        from models import Notification
        
        # Get the parties involved in the contract
        student = contract.student
        coach = contract.coach
        
        if notification_type == 'contract_sent':
            # Notify student that contract was sent
            Notification.create_notification(
                user_id=student.id,
                title="New Contract Proposal",
                message=f"Coach {coach.first_name} {coach.last_name} has sent you a contract proposal for '{contract.learning_request.title}'",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'contract_accepted':
            # Notify coach that contract was accepted
            Notification.create_notification(
                user_id=coach.id,
                title="Contract Accepted",
                message=f"Student {student.first_name} {student.last_name} has accepted your contract for '{contract.learning_request.title}'",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'contract_rejected':
            # Notify coach that contract was rejected
            Notification.create_notification(
                user_id=coach.id,
                title="Contract Rejected",
                message=f"Student {student.first_name} {student.last_name} has rejected your contract for '{contract.learning_request.title}'",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'payment_received':
            # Notify coach that payment was received
            Notification.create_notification(
                user_id=coach.id,
                title="Payment Received",
                message=f"You have received payment for contract '{contract.learning_request.title}' from {student.first_name} {student.last_name}",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'session_scheduled':
            # Notify both parties about scheduled session
            session_info = f"Session scheduled for {contract.learning_request.title}"
            
            Notification.create_notification(
                user_id=student.id,
                title="Session Scheduled",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has been scheduled",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Scheduled",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has been scheduled",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'session_rescheduled':
            # Notify both parties about rescheduled session
            Notification.create_notification(
                user_id=student.id,
                title="Session Rescheduled",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has been rescheduled",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Rescheduled",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has been rescheduled",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'session_completed':
            # Notify both parties about completed session
            Notification.create_notification(
                user_id=student.id,
                title="Session Completed",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has been completed",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Completed",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has been completed",
                notification_type='session',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'contract_cancelled':
            # Notify both parties about cancelled contract
            Notification.create_notification(
                user_id=student.id,
                title="Contract Cancelled",
                message=f"Your contract with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has been cancelled",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Contract Cancelled",
                message=f"Your contract with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has been cancelled",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'payment_failed':
            # Notify student about failed payment
            Notification.create_notification(
                user_id=student.id,
                title="Payment Failed",
                message=f"Payment for contract '{contract.learning_request.title}' with {coach.first_name} {coach.last_name} has failed. Please try again.",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
        elif notification_type == 'contract_expired':
            # Notify both parties about expired contract
            Notification.create_notification(
                user_id=student.id,
                title="Contract Expired",
                message=f"Your contract with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has expired",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Contract Expired",
                message=f"Your contract with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has expired",
                notification_type='contract',
                related_id=contract.id,
                related_type='contract'
            )
            
    except Exception as e:
        logger.error(f"Error creating contract notification: {e}")

def create_session_notification(session, notification_type):
    """
    Create notifications for session-related events
    
    Args:
        session: Session object
        notification_type: Type of notification ('scheduled', 'rescheduled', 'cancelled', 'completed', 'reminder')
    """
    try:
        from models import Notification
        
        contract = session.contract
        student = contract.student
        coach = contract.coach
        
        if notification_type == 'session_reminder':
            # Send reminder 1 hour before session
            Notification.create_notification(
                user_id=student.id,
                title="Session Reminder",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' starts in 1 hour",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Reminder",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' starts in 1 hour",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
        elif notification_type == 'session_cancelled':
            # Notify both parties about cancelled session
            Notification.create_notification(
                user_id=student.id,
                title="Session Cancelled",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' has been cancelled",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Cancelled",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' has been cancelled",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
        elif notification_type == 'session_starting':
            # Notify both parties that session is starting
            Notification.create_notification(
                user_id=student.id,
                title="Session Starting",
                message=f"Your session with {coach.first_name} {coach.last_name} for '{contract.learning_request.title}' is starting now",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
            Notification.create_notification(
                user_id=coach.id,
                title="Session Starting",
                message=f"Your session with {student.first_name} {student.last_name} for '{contract.learning_request.title}' is starting now",
                notification_type='session',
                related_id=session.id,
                related_type='session'
            )
            
    except Exception as e:
        logger.error(f"Error creating session notification: {e}")

def create_message_notification(sender, recipient, message_preview):
    """Create notification for new messages"""
    try:
        from models import Notification
        
        Notification.create_notification(
            user_id=recipient.id,
            title="New Message",
            message=f"You have a new message from {sender.first_name} {sender.last_name}: {message_preview[:50]}...",
            notification_type='message',
            related_id=sender.id,
            related_type='user'
        )
    except Exception as e:
        logger.error(f"Error creating message notification: {e}")

def create_system_notification(user_id, title, message, notification_type='system'):
    """Create system notification"""
    try:
        from models import Notification
        
        Notification.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
    except Exception as e:
        logger.error(f"Error creating system notification: {e}")

def create_job_notification(learning_request, notification_type, proposal=None):
    """Create notifications for job-related events"""
    try:
        from models import Notification
        
        if notification_type == 'job_posted':
            # Notify relevant coaches about new job
            # This would typically involve finding coaches that match the job criteria
            pass
            
        elif notification_type == 'proposal_received':
            # Notify student about new proposal
            Notification.create_notification(
                user_id=learning_request.student_id,
                title="New Proposal Received",
                message=f"You have received a new proposal for your job '{learning_request.title}'",
                notification_type='job',
                related_id=learning_request.id,
                related_type='job'
            )
            
        elif notification_type == 'job_accepted':
            # Notify coach that their proposal was accepted
            if proposal:
                Notification.create_notification(
                    user_id=proposal.coach_id,
                    title="Proposal Accepted",
                    message=f"Your proposal for job '{learning_request.title}' has been accepted",
                    notification_type='job',
                    related_id=learning_request.id,
                    related_type='job'
                )
            
        elif notification_type == 'job_rejected':
            # Notify coach that their proposal was rejected
            if proposal:
                Notification.create_notification(
                    user_id=proposal.coach_id,
                    title="Proposal Rejected",
                    message=f"Your proposal for job '{learning_request.title}' has been rejected",
                    notification_type='job',
                    related_id=learning_request.id,
                    related_type='job'
                )
            
        elif notification_type == 'job_completed':
            # Notify both parties about completed job
            if proposal:
                Notification.create_notification(
                    user_id=learning_request.student_id,
                    title="Job Completed",
                    message=f"Your job '{learning_request.title}' with {proposal.coach.first_name} {proposal.coach.last_name} has been completed",
                    notification_type='job',
                    related_id=learning_request.id,
                    related_type='job'
                )
                
                Notification.create_notification(
                    user_id=proposal.coach_id,
                    title="Job Completed",
                    message=f"Your job '{learning_request.title}' with {learning_request.student.first_name} {learning_request.student.last_name} has been completed",
                    notification_type='job',
                    related_id=learning_request.id,
                    related_type='job'
                )
            
    except Exception as e:
        logger.error(f"Error creating job notification: {e}")

def create_profile_notification(user, notification_type):
    """Create notifications for profile-related events"""
    try:
        from models import Notification
        
        if notification_type == 'profile_updated':
            Notification.create_notification(
                user_id=user.id,
                title="Profile Updated",
                message="Your profile has been successfully updated",
                notification_type='system'
            )
            
        elif notification_type == 'role_switched':
            Notification.create_notification(
                user_id=user.id,
                title="Role Switched",
                message=f"You have successfully switched to {user.current_role} mode",
                notification_type='system'
            )
            
        elif notification_type == 'account_verified':
            Notification.create_notification(
                user_id=user.id,
                title="Account Verified",
                message="Your account has been successfully verified",
                notification_type='system'
            )
            
    except Exception as e:
        logger.error(f"Error creating profile notification: {e}")

def create_payment_notification(user, amount, status, contract_title=None):
    """Create notifications for payment-related events"""
    try:
        from models import Notification
        
        if status == 'success':
            title = "Payment Successful"
            message = f"Your payment of ${amount:.2f} has been processed successfully"
            if contract_title:
                message += f" for contract '{contract_title}'"
        elif status == 'failed':
            title = "Payment Failed"
            message = f"Your payment of ${amount:.2f} has failed. Please try again."
            if contract_title:
                message += f" for contract '{contract_title}'"
        elif status == 'refunded':
            title = "Payment Refunded"
            message = f"Your payment of ${amount:.2f} has been refunded"
            if contract_title:
                message += f" for contract '{contract_title}'"
        else:
            return
            
        Notification.create_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type='system'
        )
        
    except Exception as e:
        logger.error(f"Error creating payment notification: {e}")

def create_bulk_notification(user_ids, title, message, notification_type='system'):
    """Create notifications for multiple users at once"""
    try:
        from models import Notification
        
        for user_id in user_ids:
            Notification.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type
            )
    except Exception as e:
        logger.error(f"Error creating bulk notification: {e}")

def cleanup_old_notifications(days_old=30):
    """Clean up old notifications to keep the database clean"""
    try:
        from models import Notification
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete old read notifications
        old_notifications = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        
        return old_notifications
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {e}")
        return 0
