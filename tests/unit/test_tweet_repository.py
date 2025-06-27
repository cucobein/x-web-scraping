"""
Unit tests for TweetRepository
"""
import pytest

from src.repositories.tweet_repository import TweetRepository
from src.models.tweet import Tweet


class TestTweetRepository:
    """Test cases for TweetRepository"""
    
    def setup_method(self):
        """Set up fresh repository for each test"""
        self.repository = TweetRepository()
    
    def test_save_and_retrieve_last_tweet(self):
        """Test saving and retrieving last tweet for a user"""
        tweet = Tweet(
            username="testuser",
            content="Test tweet content",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123"
        )
        
        # Save tweet
        self.repository.save_last_tweet("testuser", tweet)
        
        # Retrieve tweet ID
        last_id = self.repository.get_last_tweet_id("testuser")
        
        assert last_id == tweet.unique_id
    
    def test_get_last_tweet_id_for_new_user(self):
        """Test getting last tweet ID for user that hasn't been tracked"""
        last_id = self.repository.get_last_tweet_id("newuser")
        
        assert last_id is None
    
    def test_has_new_tweet_for_first_time_user(self):
        """Test has_new_tweet for first time user (should return True)"""
        tweet = Tweet(
            username="newuser",
            content="First tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        has_new = self.repository.has_new_tweet("newuser", tweet)
        
        assert has_new is True
    
    def test_has_new_tweet_same_tweet(self):
        """Test has_new_tweet for same tweet (should return False)"""
        tweet = Tweet(
            username="testuser",
            content="Same tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Save tweet first
        self.repository.save_last_tweet("testuser", tweet)
        
        # Check same tweet again
        has_new = self.repository.has_new_tweet("testuser", tweet)
        
        assert has_new is False
    
    def test_has_new_tweet_different_tweet(self):
        """Test has_new_tweet for different tweet (should return True)"""
        tweet1 = Tweet(
            username="testuser",
            content="First tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        tweet2 = Tweet(
            username="testuser",
            content="Second tweet",
            timestamp="2024-01-15T10:35:00Z"
        )
        
        # Save first tweet
        self.repository.save_last_tweet("testuser", tweet1)
        
        # Check second tweet
        has_new = self.repository.has_new_tweet("testuser", tweet2)
        
        assert has_new is True
    
    def test_get_all_tracked_users(self):
        """Test getting list of all tracked users"""
        # Initially empty
        users = self.repository.get_all_tracked_users()
        assert users == []
        
        # Add some users
        tweet1 = Tweet("user1", "content1", "2024-01-15T10:30:00Z")
        tweet2 = Tweet("user2", "content2", "2024-01-15T10:35:00Z")
        
        self.repository.save_last_tweet("user1", tweet1)
        self.repository.save_last_tweet("user2", tweet2)
        
        users = self.repository.get_all_tracked_users()
        assert len(users) == 2
        assert "user1" in users
        assert "user2" in users
    
    def test_clear_repository(self):
        """Test clearing all stored data"""
        # Add some data
        tweet = Tweet("testuser", "content", "2024-01-15T10:30:00Z")
        self.repository.save_last_tweet("testuser", tweet)
        
        # Verify data exists
        assert self.repository.get_last_tweet_id("testuser") is not None
        
        # Clear repository
        self.repository.clear()
        
        # Verify data is gone
        assert self.repository.get_last_tweet_id("testuser") is None
        assert self.repository.get_all_tracked_users() == []
    
    def test_multiple_users_independent_tracking(self):
        """Test that tracking is independent between users"""
        tweet1 = Tweet("user1", "content1", "2024-01-15T10:30:00Z")
        tweet2 = Tweet("user2", "content2", "2024-01-15T10:35:00Z")
        
        # Save tweets for different users
        self.repository.save_last_tweet("user1", tweet1)
        self.repository.save_last_tweet("user2", tweet2)
        
        # Verify each user has their own tracking
        assert self.repository.get_last_tweet_id("user1") == tweet1.unique_id
        assert self.repository.get_last_tweet_id("user2") == tweet2.unique_id
        
        # Verify users list
        users = self.repository.get_all_tracked_users()
        assert len(users) == 2
        assert "user1" in users
        assert "user2" in users
    
    def test_tweet_with_url_tracking(self):
        """Test tracking tweets with URLs"""
        tweet = Tweet(
            username="testuser",
            content="Tweet with URL",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123456789"
        )
        
        self.repository.save_last_tweet("testuser", tweet)
        
        last_id = self.repository.get_last_tweet_id("testuser")
        assert last_id == tweet.unique_id
        
        # URL should NOT be part of the unique ID (it's based on content + timestamp)
        assert "123456789" not in last_id
        assert "Tweet with URL" in last_id 