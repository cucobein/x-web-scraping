"""
Data models for X Feed Monitor
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Tweet:
    """Represents a tweet"""

    username: str
    content: str
    timestamp: str
    url: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate tweet data"""
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.content:
            raise ValueError("Content cannot be empty")
        if not self.timestamp:
            raise ValueError("Timestamp cannot be empty")

    @property
    def unique_id(self) -> str:
        """Generate unique identifier for this tweet"""
        if self.url:
            # Extract tweet ID from URL: https://x.com/username/status/123456789
            # The status number is the unique tweet ID
            return self.url
        else:
            # Fallback to content + timestamp if no URL available
            return f"{self.content[:50]}_{self.timestamp}"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tweet":
        """Create Tweet from dictionary"""
        return cls(
            username=data["username"],
            content=data["content"],
            timestamp=data["timestamp"],
            url=data.get("url"),
        )
