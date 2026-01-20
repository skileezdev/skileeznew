"""
Enhanced API Manager for Phase 5B
Handles rate limiting, error handling, webhook support, and enhanced API endpoints
"""

import logging
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from flask import request, jsonify, current_app
from models import Session, ScheduledCall, User, Contract, db

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, count), ...]}
        self.max_requests = 100  # requests per window
        self.window_seconds = 3600  # 1 hour window
    
    def is_allowed(self, ip: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Clean old requests outside window
        self.requests[ip] = [
            (ts, count) for ts, count in self.requests[ip] 
            if now - ts < self.window_seconds
        ]
        
        # Count total requests in window
        total_requests = sum(count for _, count in self.requests[ip])
        
        if total_requests >= self.max_requests:
            return False
        
        # Add current request
        self.requests[ip].append((now, 1))
        return True
    
    def get_remaining_requests(self, ip: str) -> int:
        """Get remaining requests for an IP"""
        now = time.time()
        
        if ip not in self.requests:
            return self.max_requests
        
        # Clean old requests
        self.requests[ip] = [
            (ts, count) for ts, count in self.requests[ip] 
            if now - ts < self.window_seconds
        ]
        
        total_requests = sum(count for _, count in self.requests[ip])
        return max(0, self.max_requests - total_requests)

class WebhookManager:
    """Manages webhook subscriptions and deliveries"""
    
    def __init__(self):
        self.webhooks = {}  # {event_type: [webhook_urls]}
        self.secret_key = "your-webhook-secret-key"  # In production, use environment variable
    
    def register_webhook(self, event_type: str, webhook_url: str) -> bool:
        """Register a webhook for an event type"""
        try:
            if event_type not in self.webhooks:
                self.webhooks[event_type] = []
            
            if webhook_url not in self.webhooks[event_type]:
                self.webhooks[event_type].append(webhook_url)
            
            logger.info(f"Registered webhook for {event_type}: {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            return False
    
    def unregister_webhook(self, event_type: str, webhook_url: str) -> bool:
        """Unregister a webhook"""
        try:
            if event_type in self.webhooks and webhook_url in self.webhooks[event_type]:
                self.webhooks[event_type].remove(webhook_url)
                logger.info(f"Unregistered webhook for {event_type}: {webhook_url}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unregistering webhook: {e}")
            return False
    
    def send_webhook(self, event_type: str, data: Dict[str, Any]) -> List[bool]:
        """Send webhook notifications for an event"""
        results = []
        
        if event_type not in self.webhooks:
            return results
        
        # Create webhook payload
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        # Add signature
        signature = self._create_signature(payload)
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'User-Agent': 'Skileez-Webhook/1.0'
        }
        
        # Send to all registered webhooks
        import requests
        for webhook_url in self.webhooks[event_type]:
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                success = response.status_code in [200, 201, 202]
                results.append(success)
                
                if success:
                    logger.info(f"Webhook sent successfully to {webhook_url}")
                else:
                    logger.warning(f"Webhook failed to {webhook_url}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error sending webhook to {webhook_url}: {e}")
                results.append(False)
        
        return results
    
    def _create_signature(self, payload: Dict[str, Any]) -> str:
        """Create HMAC signature for webhook payload"""
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

class APIError(Exception):
    """Custom API error class"""
    
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class APIManager:
    """Main API manager for enhanced endpoints and functionality"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.webhook_manager = WebhookManager()
        self.api_version = "v1"
    
    def rate_limit(self, f: Callable) -> Callable:
        """Decorator for rate limiting"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.remote_addr
            
            if not self.rate_limiter.is_allowed(ip):
                remaining = self.rate_limiter.get_remaining_requests(ip)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.',
                    'retry_after': 3600,
                    'remaining_requests': remaining
                }), 429
            
            # Add rate limit headers
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response_obj, status_code = response
            else:
                response_obj = response
                status_code = 200
            
            remaining = self.rate_limiter.get_remaining_requests(ip)
            response_obj.headers['X-RateLimit-Remaining'] = str(remaining)
            response_obj.headers['X-RateLimit-Limit'] = str(self.rate_limiter.max_requests)
            response_obj.headers['X-RateLimit-Reset'] = str(int(time.time() + self.rate_limiter.window_seconds))
            
            return response_obj, status_code
        
        return decorated_function
    
    def handle_errors(self, f: Callable) -> Callable:
        """Decorator for error handling"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except APIError as e:
                return jsonify({
                    'error': e.error_code or 'api_error',
                    'message': e.message,
                    'status_code': e.status_code
                }), e.status_code
            except Exception as e:
                logger.error(f"API error in {f.__name__}: {e}")
                return jsonify({
                    'error': 'internal_error',
                    'message': 'An internal error occurred',
                    'status_code': 500
                }), 500
        
        return decorated_function
    
    def validate_json(self, required_fields: List[str] = None) -> Callable:
        """Decorator for JSON validation"""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not request.is_json:
                    raise APIError("Content-Type must be application/json", 400, "invalid_content_type")
                
                data = request.get_json()
                if data is None:
                    raise APIError("Invalid JSON data", 400, "invalid_json")
                
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        raise APIError(f"Missing required fields: {', '.join(missing_fields)}", 400, "missing_fields")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def get_session_data(self, session_id: int) -> Dict[str, Any]:
        """Get enhanced session data"""
        try:
            session = Session.query.get_or_404(session_id)
            
            # Get related data
            contract = session.get_contract()
            coach = contract.coach if contract else None
            student = contract.student if contract else None
            
            return {
                'id': session.id,
                'status': session.status,
                'scheduled_at': session.scheduled_at.isoformat() if session.scheduled_at else None,
                'duration_minutes': session.duration_minutes,
                'session_number': session.session_number,
                'meeting_started_at': session.meeting_started_at.isoformat() if session.meeting_started_at else None,
                'meeting_ended_at': session.meeting_ended_at.isoformat() if session.meeting_ended_at else None,
                'early_join_enabled': session.early_join_enabled,
                'waiting_room_enabled': session.waiting_room_enabled,
                'buffer_minutes': session.buffer_minutes,
                'reminder_sent': session.reminder_sent,
                'auto_activated': session.auto_activated,
                'can_join_early': session.can_join_early(),
                'contract': {
                    'id': contract.id if contract else None,
                    'status': contract.status if contract else None,
                    'payment_status': contract.payment_status if contract else None
                },
                'coach': {
                    'id': coach.user.id if coach else None,
                    'name': f"{coach.user.first_name} {coach.user.last_name}" if coach else None,
                    'email': coach.user.email if coach else None
                },
                'student': {
                    'id': student.user.id if student else None,
                    'name': f"{student.user.first_name} {student.user.last_name}" if student else None,
                    'email': student.user.email if student else None
                },
                'learning_request': {
                    'title': session.proposal.learning_request.title if session.proposal else None,
                    'description': session.proposal.learning_request.description if session.proposal else None
                } if session.proposal else None
            }
            
        except Exception as e:
            logger.error(f"Error getting session data: {e}")
            raise APIError("Error retrieving session data", 500, "session_retrieval_error")
    
    def get_user_sessions(self, user_id: int, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get sessions for a user with optional filtering"""
        try:
            query = Session.query.join(Session.proposal).join(Contract).filter(
                (Contract.coach_id == user_id) | (Contract.student_id == user_id)
            )
            
            if status:
                query = query.filter(Session.status == status)
            
            sessions = query.order_by(Session.scheduled_at.desc()).limit(limit).all()
            
            return [self.get_session_data(session.id) for session in sessions]
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            raise APIError("Error retrieving user sessions", 500, "user_sessions_retrieval_error")
    
    def update_session_status(self, session_id: int, status: str, reason: str = None) -> Dict[str, Any]:
        """Update session status with webhook notification"""
        try:
            session = Session.query.get_or_404(session_id)
            old_status = session.status
            session.status = status
            
            if status == 'active':
                session.meeting_started_at = datetime.utcnow()
            elif status == 'completed':
                session.meeting_ended_at = datetime.utcnow()
            
            db.session.commit()
            
            # Send webhook notification
            webhook_data = {
                'session_id': session_id,
                'old_status': old_status,
                'new_status': status,
                'reason': reason,
                'updated_at': datetime.utcnow().isoformat()
            }
            self.webhook_manager.send_webhook('session_status_changed', webhook_data)
            
            return self.get_session_data(session_id)
            
        except Exception as e:
            logger.error(f"Error updating session status: {e}")
            raise APIError("Error updating session status", 500, "session_update_error")

# Global API manager instance
api_manager = APIManager()

def get_api_manager() -> APIManager:
    """Get the global API manager instance"""
    return api_manager

def create_api_response(data: Any = None, message: str = None, status_code: int = 200) -> tuple:
    """Create standardized API response"""
    response = {
        'success': status_code < 400,
        'timestamp': datetime.utcnow().isoformat(),
        'api_version': api_manager.api_version
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

def validate_webhook_signature(request_data: bytes, signature: str) -> bool:
    """Validate webhook signature"""
    try:
        expected_signature = hmac.new(
            api_manager.webhook_manager.secret_key.encode('utf-8'),
            request_data,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
        
    except Exception as e:
        logger.error(f"Error validating webhook signature: {e}")
        return False
