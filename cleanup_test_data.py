#!/usr/bin/env python3
"""
Clean up test data from the database
"""

from app import app, db
from models import Contract, Proposal, LearningRequest, User, StudentProfile, CoachProfile

def cleanup_test_data():
    """Clean up test data"""
    with app.app_context():
        print("🧹 Cleaning up test data...")
        
        # Delete contracts
        contracts = Contract.query.all()
        for contract in contracts:
            db.session.delete(contract)
        print(f"✅ Deleted {len(contracts)} contracts")
        
        # Delete proposals
        proposals = Proposal.query.all()
        for proposal in proposals:
            db.session.delete(proposal)
        print(f"✅ Deleted {len(proposals)} proposals")
        
        # Delete learning requests
        learning_requests = LearningRequest.query.all()
        for lr in learning_requests:
            db.session.delete(lr)
        print(f"✅ Deleted {len(learning_requests)} learning requests")
        
        # Delete test users
        test_users = User.query.filter(User.email.like('%payment_test%')).all()
        for user in test_users:
            db.session.delete(user)
        print(f"✅ Deleted {len(test_users)} test users")
        
        # Delete profiles
        student_profiles = StudentProfile.query.all()
        for sp in student_profiles:
            db.session.delete(sp)
        print(f"✅ Deleted {len(student_profiles)} student profiles")
        
        coach_profiles = CoachProfile.query.all()
        for cp in coach_profiles:
            db.session.delete(cp)
        print(f"✅ Deleted {len(coach_profiles)} coach profiles")
        
        db.session.commit()
        print("🎉 Database cleanup completed!")

if __name__ == "__main__":
    cleanup_test_data()
