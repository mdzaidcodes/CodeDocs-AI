"""
User Quota Model
Tracks daily project creation limits for users.
"""

from datetime import datetime, timedelta
import pytz
from config.database import get_db_cursor


class UserQuota:
    """Model for managing user daily quotas."""
    
    @staticmethod
    def get_user_quota(user_id):
        """
        Get current day's quota usage for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Quota information with projects_created_today and quota_date
        """
        # Get current date in GMT+4
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_date = datetime.now(gmt_plus_4).date()
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, quota_date, projects_created_today, messages_sent_today, created_at, updated_at
                FROM user_quotas
                WHERE user_id = %s AND quota_date = %s
            """, (user_id, current_date))
            
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            else:
                # No quota record for today, return default
                return {
                    'user_id': user_id,
                    'quota_date': current_date,
                    'projects_created_today': 0,
                    'messages_sent_today': 0,
                    'created_at': None,
                    'updated_at': None
                }
    
    @staticmethod
    def increment_quota(user_id):
        """
        Increment the project creation count for today.
        Creates a new record if one doesn't exist for today.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Updated quota information
        """
        # Get current date in GMT+4
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_date = datetime.now(gmt_plus_4).date()
        
        with get_db_cursor(commit=True) as cursor:
            # Try to get existing quota for today
            cursor.execute("""
                SELECT user_id, quota_date, projects_created_today
                FROM user_quotas
                WHERE user_id = %s AND quota_date = %s
            """, (user_id, current_date))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing quota
                cursor.execute("""
                    UPDATE user_quotas
                    SET projects_created_today = projects_created_today + 1,
                        updated_at = NOW()
                    WHERE user_id = %s AND quota_date = %s
                    RETURNING user_id, quota_date, projects_created_today, updated_at
                """, (user_id, current_date))
            else:
                # Create new quota record for today
                cursor.execute("""
                    INSERT INTO user_quotas (user_id, quota_date, projects_created_today)
                    VALUES (%s, %s, 1)
                    RETURNING user_id, quota_date, projects_created_today, created_at
                """, (user_id, current_date))
            
            result = cursor.fetchone()
            return dict(result)
    
    @staticmethod
    def check_quota_available(user_id, max_projects=3):
        """
        Check if user has available quota to create a project.
        
        Args:
            user_id: User ID
            max_projects: Maximum projects allowed per day (default: 3)
            
        Returns:
            tuple: (bool: has_quota, int: remaining_quota, datetime: reset_time)
        """
        quota_info = UserQuota.get_user_quota(user_id)
        projects_created = quota_info['projects_created_today']
        
        has_quota = projects_created < max_projects
        remaining = max(0, max_projects - projects_created)
        
        # Calculate reset time (midnight GMT+4)
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_time = datetime.now(gmt_plus_4)
        next_midnight = (current_time + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        return has_quota, remaining, next_midnight
    
    @staticmethod
    def get_quota_stats(user_id):
        """
        Get quota statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Quota statistics including current, max, remaining, and reset time
        """
        max_projects = 3
        has_quota, remaining, reset_time = UserQuota.check_quota_available(user_id, max_projects)
        quota_info = UserQuota.get_user_quota(user_id)
        
        return {
            'projects_created_today': quota_info['projects_created_today'],
            'max_projects_per_day': max_projects,
            'remaining_quota': remaining,
            'has_quota': has_quota,
            'quota_reset_at': reset_time.isoformat(),
            'timezone': 'GMT+4'
        }
    
    @staticmethod
    def cleanup_old_quotas(days_to_keep=30):
        """
        Clean up old quota records to keep database tidy.
        Keeps records from the last N days.
        
        Args:
            days_to_keep: Number of days to keep (default: 30)
            
        Returns:
            int: Number of records deleted
        """
        # Get current date in GMT+4
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_date = datetime.now(gmt_plus_4).date()
        cutoff_date = current_date - timedelta(days=days_to_keep)
        
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM user_quotas
                WHERE quota_date < %s
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            return deleted_count
    
    # =========================================================================
    # Chat Message Quota Methods
    # =========================================================================
    
    @staticmethod
    def increment_message_quota(user_id):
        """
        Increment the chat message count for today.
        Creates a new record if one doesn't exist for today.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Updated quota information
        """
        # Get current date in GMT+4
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_date = datetime.now(gmt_plus_4).date()
        
        with get_db_cursor(commit=True) as cursor:
            # Try to get existing quota for today
            cursor.execute("""
                SELECT user_id, quota_date, messages_sent_today
                FROM user_quotas
                WHERE user_id = %s AND quota_date = %s
            """, (user_id, current_date))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing quota
                cursor.execute("""
                    UPDATE user_quotas
                    SET messages_sent_today = messages_sent_today + 1,
                        updated_at = NOW()
                    WHERE user_id = %s AND quota_date = %s
                    RETURNING user_id, quota_date, messages_sent_today, updated_at
                """, (user_id, current_date))
            else:
                # Create new quota record for today
                cursor.execute("""
                    INSERT INTO user_quotas (user_id, quota_date, messages_sent_today)
                    VALUES (%s, %s, 1)
                    RETURNING user_id, quota_date, messages_sent_today, created_at
                """, (user_id, current_date))
            
            result = cursor.fetchone()
            return dict(result)
    
    @staticmethod
    def check_message_quota_available(user_id, max_messages=5):
        """
        Check if user has available quota to send a chat message.
        
        Args:
            user_id: User ID
            max_messages: Maximum messages allowed per day (default: 5)
            
        Returns:
            tuple: (bool: has_quota, int: remaining_quota, datetime: reset_time)
        """
        quota_info = UserQuota.get_user_quota(user_id)
        messages_sent = quota_info['messages_sent_today']
        
        has_quota = messages_sent < max_messages
        remaining = max(0, max_messages - messages_sent)
        
        # Calculate reset time (midnight GMT+4)
        gmt_plus_4 = pytz.timezone('Etc/GMT-4')
        current_time = datetime.now(gmt_plus_4)
        next_midnight = (current_time + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        return has_quota, remaining, next_midnight
    
    @staticmethod
    def get_message_quota_stats(user_id):
        """
        Get message quota statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Message quota statistics including current, max, remaining, and reset time
        """
        max_messages = 5
        has_quota, remaining, reset_time = UserQuota.check_message_quota_available(user_id, max_messages)
        quota_info = UserQuota.get_user_quota(user_id)
        
        return {
            'messages_sent_today': quota_info['messages_sent_today'],
            'max_messages_per_day': max_messages,
            'remaining_quota': remaining,
            'has_quota': has_quota,
            'quota_reset_at': reset_time.isoformat(),
            'timezone': 'GMT+4'
        }

