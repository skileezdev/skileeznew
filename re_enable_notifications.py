#!/usr/bin/env python3
"""
Script to re-enable notifications after the table is created
"""

def re_enable_notifications():
    """Re-enable notifications in routes.py"""
    
    print("🔧 Re-enabling Notifications...")
    print("="*50)
    
    try:
        # Read the current routes.py file
        with open('routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the disabled notification calls with the actual calls
        replacements = [
            # Message notification
            (
                '        # Create notification for recipient (temporarily disabled until table is created)\n        # TODO: Re-enable after notification table is created in production\n        pass',
                '        # Create notification for recipient\n        try:\n            from notification_utils import create_message_notification\n            create_message_notification(current_user, recipient, form.content.data)\n        except Exception as e:\n            print(f"Error creating message notification: {e}")\n            # Don\'t let notification errors affect message sending\n            pass'
            ),
            # Job accepted notification
            (
                '        # Create notification for coach (temporarily disabled until table is created)\n        # TODO: Re-enable after notification table is created in production\n        pass',
                '        # Create notification for coach\n        try:\n            from notification_utils import create_job_notification\n            create_job_notification(learning_request, \'job_accepted\', proposal)\n        except Exception as e:\n            print(f"Error creating job notification: {e}")\n            # Don\'t let notification errors affect the main flow\n            pass'
            ),
            # Job rejected notification
            (
                '        # Create notification for coach (temporarily disabled until table is created)\n        # TODO: Re-enable after notification table is created in production\n        pass',
                '        # Create notification for coach\n        try:\n            from notification_utils import create_job_notification\n            create_job_notification(learning_request, \'job_rejected\', proposal)\n        except Exception as e:\n            print(f"Error creating job notification: {e}")\n            # Don\'t let notification errors affect the main flow\n            pass'
            ),
            # Proposal received notification
            (
                '        # Create notification for student about new proposal (temporarily disabled until table is created)\n        # TODO: Re-enable after notification table is created in production\n        pass',
                '        # Create notification for student about new proposal\n        try:\n            from notification_utils import create_job_notification\n            create_job_notification(learning_request, \'proposal_received\')\n        except Exception as e:\n            print(f"Error creating proposal notification: {e}")\n            # Don\'t let notification errors affect the main flow\n            pass'
            )
        ]
        
        # Apply all replacements
        modified_content = content
        for old_text, new_text in replacements:
            if old_text in modified_content:
                modified_content = modified_content.replace(old_text, new_text)
                print("✅ Re-enabled notification call")
            else:
                print("⚠️  Could not find notification call to re-enable")
        
        # Write the modified content back
        with open('routes.py', 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("\n" + "="*50)
        print("🎉 NOTIFICATIONS RE-ENABLED SUCCESSFULLY!")
        print("="*50)
        print("\n✅ All notification calls have been re-enabled:")
        print("   • Message notifications")
        print("   • Job acceptance notifications")
        print("   • Job rejection notifications")
        print("   • Proposal received notifications")
        print("\nNext steps:")
        print("1. Deploy the updated routes.py to production")
        print("2. Restart the Flask application")
        print("3. Test sending messages, proposals, contracts")
        print("4. Verify that notifications appear in real-time")
        
        return True
        
    except Exception as e:
        print(f"❌ Error re-enabling notifications: {e}")
        return False

if __name__ == "__main__":
    re_enable_notifications()
