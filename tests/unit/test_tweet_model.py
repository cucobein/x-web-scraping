"""
Unit tests for Tweet model
"""
import pytest
from datetime import datetime

from src.models.tweet import Tweet


class TestTweetModel:
    """Test cases for Tweet model"""
    
    def test_tweet_creation_with_valid_data(self):
        """Test creating a tweet with valid data"""
        tweet = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123456789"
        )
        
        assert tweet.username == "testuser"
        assert tweet.content == "This is a test tweet"
        assert tweet.timestamp == "2024-01-15T10:30:00Z"
        assert tweet.url == "https://x.com/testuser/status/123456789"
    
    def test_tweet_creation_without_url(self):
        """Test creating a tweet without URL (optional field)"""
        tweet = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert tweet.username == "testuser"
        assert tweet.content == "This is a test tweet"
        assert tweet.timestamp == "2024-01-15T10:30:00Z"
        assert tweet.url is None
    
    def test_tweet_validation_empty_username(self):
        """Test that empty username raises ValueError"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            Tweet(
                username="",
                content="This is a test tweet",
                timestamp="2024-01-15T10:30:00Z"
            )
    
    def test_tweet_validation_empty_content(self):
        """Test that empty content raises ValueError"""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            Tweet(
                username="testuser",
                content="",
                timestamp="2024-01-15T10:30:00Z"
            )
    
    def test_tweet_validation_empty_timestamp(self):
        """Test that empty timestamp raises ValueError"""
        with pytest.raises(ValueError, match="Timestamp cannot be empty"):
            Tweet(
                username="testuser",
                content="This is a test tweet",
                timestamp=""
            )
    
    def test_tweet_unique_id_generation(self):
        """Test that unique_id is generated correctly"""
        tweet = Tweet(
            username="testuser",
            content="This is a very long tweet content that should be truncated for the unique ID",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Should be first 50 chars of content + timestamp
        expected_id = "This is a very long tweet content that should be t_2024-01-15T10:30:00Z"
        assert tweet.unique_id == expected_id
    
    def test_tweet_unique_id_with_short_content(self):
        """Test unique_id with content shorter than 50 characters"""
        tweet = Tweet(
            username="testuser",
            content="Short tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        expected_id = "Short tweet_2024-01-15T10:30:00Z"
        assert tweet.unique_id == expected_id
    
    def test_tweet_to_dict(self):
        """Test converting tweet to dictionary"""
        tweet = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123456789"
        )
        
        tweet_dict = tweet.to_dict()
        
        assert tweet_dict == {
            "username": "testuser",
            "content": "This is a test tweet",
            "timestamp": "2024-01-15T10:30:00Z",
            "url": "https://x.com/testuser/status/123456789"
        }
    
    def test_tweet_to_dict_without_url(self):
        """Test converting tweet to dictionary without URL"""
        tweet = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        tweet_dict = tweet.to_dict()
        
        assert tweet_dict == {
            "username": "testuser",
            "content": "This is a test tweet",
            "timestamp": "2024-01-15T10:30:00Z",
            "url": None
        }
    
    def test_tweet_from_dict(self):
        """Test creating tweet from dictionary"""
        tweet_dict = {
            "username": "testuser",
            "content": "This is a test tweet",
            "timestamp": "2024-01-15T10:30:00Z",
            "url": "https://x.com/testuser/status/123456789"
        }
        
        tweet = Tweet.from_dict(tweet_dict)
        
        assert tweet.username == "testuser"
        assert tweet.content == "This is a test tweet"
        assert tweet.timestamp == "2024-01-15T10:30:00Z"
        assert tweet.url == "https://x.com/testuser/status/123456789"
    
    def test_tweet_from_dict_without_url(self):
        """Test creating tweet from dictionary without URL"""
        tweet_dict = {
            "username": "testuser",
            "content": "This is a test tweet",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        tweet = Tweet.from_dict(tweet_dict)
        
        assert tweet.username == "testuser"
        assert tweet.content == "This is a test tweet"
        assert tweet.timestamp == "2024-01-15T10:30:00Z"
        assert tweet.url is None
    
    def test_tweet_equality(self):
        """Test tweet equality"""
        tweet1 = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123456789"
        )
        
        tweet2 = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z",
            url="https://x.com/testuser/status/123456789"
        )
        
        # Should have same unique_id
        assert tweet1.unique_id == tweet2.unique_id
    
    def test_tweet_inequality_different_content(self):
        """Test tweet inequality with different content"""
        tweet1 = Tweet(
            username="testuser",
            content="This is a test tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        tweet2 = Tweet(
            username="testuser",
            content="This is a different tweet",
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Should have different unique_id
        assert tweet1.unique_id != tweet2.unique_id 