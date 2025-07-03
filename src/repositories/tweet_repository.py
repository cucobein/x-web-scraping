"""
Tweet repository for data persistence
"""

from typing import Dict, Optional

from src.models.tweet import Tweet


class TweetRepository:
    """Manages tweet data persistence"""

    def __init__(self):
        self._last_tweets: Dict[str, str] = {}

    def get_last_tweet_id(self, username: str) -> Optional[str]:
        """
        Get the last tweet ID for a username

        Args:
            username: Twitter username

        Returns:
            Last tweet ID or None if not found
        """
        return self._last_tweets.get(username)

    def save_last_tweet(self, username: str, tweet: Tweet):
        """
        Save the last tweet for a username

        Args:
            username: Twitter username
            tweet: Tweet object
        """
        self._last_tweets[username] = tweet.unique_id

    def has_new_tweet(self, username: str, tweet: Tweet) -> bool:
        """
        Check if this is a new tweet for the username

        Args:
            username: Twitter username
            tweet: Tweet to check

        Returns:
            True if this is a new tweet
        """
        last_id = self.get_last_tweet_id(username)
        if last_id is None:
            return True
        return tweet.unique_id != last_id

    def get_all_tracked_users(self) -> list:
        """Get list of all tracked usernames"""
        return list(self._last_tweets.keys())

    def clear(self):
        """Clear all stored tweet data"""
        self._last_tweets.clear()
