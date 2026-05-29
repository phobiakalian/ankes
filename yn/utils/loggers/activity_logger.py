"""
Activity Logger module for Yn Security Bot.
Tracks user activity, violations, mutes, kicks, and generates reports.
Uses MongoDB-like API provided by yn.utils.db.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ActivityLogger:
    """
    Logger class for tracking user activity and generating reports.
    Uses MongoDB-like API for database operations.
    """
    
    def __init__(self, db_connection):
        """
        Initialize ActivityLogger.
        
        Args:
            db_connection: Database connection object (MongoDB-like API)
        """
        self.db = db_connection
        # Note: Tables are created automatically by YnDB
    
    def log_message(self, chat_id: int, user_id: int, username: Optional[str] = None):
        """
        Log a message from a user.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            username: Username (optional)
        """
        try:
            # Check if user exists in stats
            existing = self.db.find({"chat_id": chat_id, "user_id": user_id})
            if not existing:
                self.db.insert_one({
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "username": username,
                    "messages": 1,
                    "violations": 0,
                    "last_active": datetime.now().isoformat()
                })
            else:
                self.db.update_one(
                    {"chat_id": chat_id, "user_id": user_id},
                    {
                        "$inc": {"messages": 1},
                        "$set": {
                            "username": username or existing[0].get("username"),
                            "last_active": datetime.now().isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    def log_violation(self, chat_id: int, user_id: int, violation_type: str, reason: Optional[str] = None):
        """
        Log a violation by a user.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            violation_type: Type of violation (forward, link, command, etc.)
            reason: Reason for the violation (optional)
        """
        try:
            # Log to violations collection
            self.db.insert_one({
                "chat_id": chat_id,
                "user_id": user_id,
                "violation_type": violation_type,
                "reason": reason,
                "created_at": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error logging violation: {e}")
    
    def log_action(self, chat_id: int, user_id: int, action_type: str, 
                   duration: Optional[str] = None, reason: Optional[str] = None, 
                   admin_id: Optional[int] = None):
        """
        Log an admin action (mute, ban, kick, etc.).
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            action_type: Type of action (mute, ban, kick, unmute, unban)
            duration: Duration of the action (optional)
            reason: Reason for the action (optional)
            admin_id: Admin who performed the action (optional)
        """
        try:
            self.db.insert_one({
                "chat_id": chat_id,
                "user_id": user_id,
                "action_type": action_type,
                "duration": duration,
                "reason": reason,
                "admin_id": admin_id,
                "created_at": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    def log_message_deletion(self, chat_id: int):
        """
        Log a message deletion.
        
        Args:
            chat_id: Chat ID
        """
        try:
            # Get or create dashboard stats
            stats = self.db.find({"chat_id": chat_id, "_type": "dashboard"})
            today = datetime.now().date().isoformat()
            
            if not stats:
                self.db.insert_one({
                    "chat_id": chat_id,
                    "_type": "dashboard",
                    "new_members_today": 0,
                    "messages_deleted_today": 1,
                    "violations_today": 0,
                    "warnings_today": 0,
                    "mutes_today": 0,
                    "bans_today": 0,
                    "last_reset": today,
                    "last_updated": datetime.now().isoformat()
                })
            else:
                stat = stats[0]
                if stat.get("last_reset") != today:
                    # Reset daily stats
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$set": {
                                "new_members_today": 0,
                                "messages_deleted_today": 1,
                                "violations_today": 0,
                                "warnings_today": 0,
                                "mutes_today": 0,
                                "bans_today": 0,
                                "last_reset": today,
                                "last_updated": datetime.now().isoformat()
                            }
                        }
                    )
                else:
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$inc": {"messages_deleted_today": 1},
                            "$set": {"last_updated": datetime.now().isoformat()}
                        }
                    )
        except Exception as e:
            logger.error(f"Error logging message deletion: {e}")
    
    def log_new_member(self, chat_id: int):
        """
        Log a new member joining.
        
        Args:
            chat_id: Chat ID
        """
        try:
            stats = self.db.find({"chat_id": chat_id, "_type": "dashboard"})
            today = datetime.now().date().isoformat()
            
            if not stats:
                self.db.insert_one({
                    "chat_id": chat_id,
                    "_type": "dashboard",
                    "new_members_today": 1,
                    "messages_deleted_today": 0,
                    "violations_today": 0,
                    "warnings_today": 0,
                    "mutes_today": 0,
                    "bans_today": 0,
                    "last_reset": today,
                    "last_updated": datetime.now().isoformat()
                })
            else:
                stat = stats[0]
                if stat.get("last_reset") != today:
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$set": {
                                "new_members_today": 1,
                                "messages_deleted_today": 0,
                                "violations_today": 0,
                                "warnings_today": 0,
                                "mutes_today": 0,
                                "bans_today": 0,
                                "last_reset": today,
                                "last_updated": datetime.now().isoformat()
                            }
                        }
                    )
                else:
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$inc": {"new_members_today": 1},
                            "$set": {"last_updated": datetime.now().isoformat()}
                        }
                    )
        except Exception as e:
            logger.error(f"Error logging new member: {e}")
    
    def log_warning(self, chat_id: int):
        """
        Log a warning given to a user.
        
        Args:
            chat_id: Chat ID
        """
        try:
            stats = self.db.find({"chat_id": chat_id, "_type": "dashboard"})
            today = datetime.now().date().isoformat()
            
            if stats:
                stat = stats[0]
                if stat.get("last_reset") != today:
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$set": {
                                "warnings_today": 1,
                                "last_reset": today,
                                "last_updated": datetime.now().isoformat()
                            }
                        }
                    )
                else:
                    self.db.update_one(
                        {"chat_id": chat_id, "_type": "dashboard"},
                        {
                            "$inc": {"warnings_today": 1},
                            "$set": {"last_updated": datetime.now().isoformat()}
                        }
                    )
        except Exception as e:
            logger.error(f"Error logging warning: {e}")
    
    def get_most_active_users(self, chat_id: int, limit: int = 10, 
                              period_days: int = 7) -> List[Tuple[int, str, int]]:
        """
        Get the most active users in a chat.
        
        Args:
            chat_id: Chat ID
            limit: Maximum number of users to return
            period_days: Number of days to look back
        
        Returns:
            List of tuples (user_id, username, message_count)
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            # Get all users for this chat
            users = self.db.find({"chat_id": chat_id})
            
            # Filter by last_active and sort by messages
            active_users = [
                u for u in users 
                if u.get("last_active", "") >= cutoff_date
            ]
            
            # Sort by message count
            active_users.sort(key=lambda x: x.get("messages", 0), reverse=True)
            
            # Return top users
            result = []
            for user in active_users[:limit]:
                result.append((
                    user.get("user_id"),
                    user.get("username", ""),
                    user.get("messages", 0)
                ))
            
            return result
        except Exception as e:
            logger.error(f"Error getting most active users: {e}")
            return []
    
    def get_most_muted_users(self, chat_id: int, limit: int = 10,
                             period_days: int = 30) -> List[Tuple[int, int]]:
        """
        Get users who were muted most frequently.
        
        Args:
            chat_id: Chat ID
            limit: Maximum number of users to return
            period_days: Number of days to look back
        
        Returns:
            List of tuples (user_id, mute_count)
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            # Get all actions for this chat
            actions = self.db.find({"chat_id": chat_id})
            
            # Filter for mute actions within period
            mute_counts = {}
            for action in actions:
                if (action.get("action_type") == "mute" and 
                    action.get("created_at", "") >= cutoff_date):
                    user_id = action.get("user_id")
                    mute_counts[user_id] = mute_counts.get(user_id, 0) + 1
            
            # Sort by count
            sorted_users = sorted(mute_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_users[:limit]
        except Exception as e:
            logger.error(f"Error getting most muted users: {e}")
            return []
    
    def get_most_kicked_users(self, chat_id: int, limit: int = 10,
                              period_days: int = 30) -> List[Tuple[int, int]]:
        """
        Get users who were kicked/banned most frequently.
        
        Args:
            chat_id: Chat ID
            limit: Maximum number of users to return
            period_days: Number of days to look back
        
        Returns:
            List of tuples (user_id, kick_count)
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            # Get all actions for this chat
            actions = self.db.find({"chat_id": chat_id})
            
            # Filter for kick/ban actions within period
            kick_counts = {}
            for action in actions:
                if (action.get("action_type") in ("kick", "ban") and 
                    action.get("created_at", "") >= cutoff_date):
                    user_id = action.get("user_id")
                    kick_counts[user_id] = kick_counts.get(user_id, 0) + 1
            
            # Sort by count
            sorted_users = sorted(kick_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_users[:limit]
        except Exception as e:
            logger.error(f"Error getting most kicked users: {e}")
            return []
    
    def get_violations_by_type(self, chat_id: int, period_days: int = 7) -> Dict[str, int]:
        """
        Get violation counts by type.
        
        Args:
            chat_id: Chat ID
            period_days: Number of days to look back
        
        Returns:
            Dictionary mapping violation types to counts
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            # Get all violations for this chat
            violations = self.db.find({"chat_id": chat_id})
            
            # Count by type
            type_counts = {}
            for v in violations:
                if v.get("created_at", "") >= cutoff_date:
                    vtype = v.get("violation_type", "unknown")
                    type_counts[vtype] = type_counts.get(vtype, 0) + 1
            
            return type_counts
        except Exception as e:
            logger.error(f"Error getting violations by type: {e}")
            return {}
    
    def get_dashboard_stats(self, chat_id: int) -> Dict[str, Any]:
        """
        Get current dashboard statistics for a chat.
        
        Args:
            chat_id: Chat ID
        
        Returns:
            Dictionary of statistics
        """
        try:
            stats = self.db.find({"chat_id": chat_id, "_type": "dashboard"})
            
            if stats:
                stat = stats[0]
                return {
                    "new_members_today": stat.get("new_members_today", 0),
                    "messages_deleted_today": stat.get("messages_deleted_today", 0),
                    "violations_today": stat.get("violations_today", 0),
                    "warnings_today": stat.get("warnings_today", 0),
                    "mutes_today": stat.get("mutes_today", 0),
                    "bans_today": stat.get("bans_today", 0),
                    "last_updated": stat.get("last_updated")
                }
            
            # Return zeros if no data
            return {
                "new_members_today": 0,
                "messages_deleted_today": 0,
                "violations_today": 0,
                "warnings_today": 0,
                "mutes_today": 0,
                "bans_today": 0,
                "last_updated": None
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                "new_members_today": 0,
                "messages_deleted_today": 0,
                "violations_today": 0,
                "warnings_today": 0,
                "mutes_today": 0,
                "bans_today": 0,
                "last_updated": None
            }
    
    def generate_activity_report(self, chat_id: int, period_days: int = 7) -> Dict:
        """
        Generate a comprehensive activity report for a chat.
        
        Args:
            chat_id: Chat ID
            period_days: Number of days for the report period
        
        Returns:
            Dictionary containing all report data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        return {
            "period_start": start_date.strftime("%Y-%m-%d"),
            "period_end": end_date.strftime("%Y-%m-%d"),
            "most_active_users": self.get_most_active_users(chat_id, period_days=period_days),
            "most_muted_users": self.get_most_muted_users(chat_id, period_days=period_days),
            "most_kicked_users": self.get_most_kicked_users(chat_id, period_days=period_days),
            "violations_by_type": self.get_violations_by_type(chat_id, period_days=period_days),
            "dashboard_stats": self.get_dashboard_stats(chat_id)
        }
    
    def get_user_violation_count(self, chat_id: int, user_id: int, 
                                 period_days: int = 30) -> int:
        """
        Get total violation count for a user.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            period_days: Number of days to look back
        
        Returns:
            Total violation count
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            violations = self.db.find({"chat_id": chat_id, "user_id": user_id})
            
            count = 0
            for v in violations:
                if v.get("created_at", "") >= cutoff_date:
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error getting user violation count: {e}")
            return 0
    
    def get_user_action_count(self, chat_id: int, user_id: int, action_type: str,
                              period_days: int = 30) -> int:
        """
        Get action count for a user.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            action_type: Type of action (mute, ban, kick)
            period_days: Number of days to look back
        
        Returns:
            Total action count
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
            
            actions = self.db.find({"chat_id": chat_id, "user_id": user_id})
            
            count = 0
            for action in actions:
                if (action.get("action_type") == action_type and 
                    action.get("created_at", "") >= cutoff_date):
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error getting user action count: {e}")
            return 0
    
    def clear_old_data(self, days_to_keep: int = 90):
        """
        Clear old data from logs to save space.
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # This would require implementing delete_many with date filtering
            # For now, just log that cleanup is needed
            logger.info(f"Data older than {days_to_keep} days should be cleaned up")
        except Exception as e:
            logger.error(f"Error clearing old data: {e}")
