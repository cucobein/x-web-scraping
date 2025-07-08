"""Firebase Logging Service for remote log storage"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore, storage

from src.utils.env_helper import get_environment


class FirebaseLogService:
    """Handles remote logging to Firebase Firestore and Storage"""

    def __init__(self, logger=None, disabled: bool = False):
        """
        Initialize Firebase Log Service

        Args:
            logger: LoggerService instance for local logging
            disabled: If True, completely disables Firebase logging (useful for tests)
        """
        self.logger = logger
        self._initialized = False
        self._enabled = False
        self._firestore_client = None
        self._storage_client = None
        
        # If explicitly disabled, don't even try to initialize
        if disabled:
            if self.logger:
                self.logger.info("Firebase logging disabled by parameter")
            return
        
        # Check if Firebase environment variables are set
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        
        # Auto-disable if Firebase config is missing
        if not self.project_id or not self.service_account_path:
            if self.logger:
                self.logger.warning(
                    "Firebase logging disabled - environment variables not set",
                    {
                        "FIREBASE_PROJECT_ID": "not_set" if not self.project_id else "set",
                        "FIREBASE_SERVICE_ACCOUNT_PATH": "not_set" if not self.service_account_path else "set"
                    }
                )
            return
        
        # Try to initialize Firebase
        try:
            self._initialize_firebase()
            self._enabled = True
            if self.logger:
                self.logger.info("Firebase logging service initialized successfully")
        except Exception as e:
            if self.logger:
                self.logger.warning(
                    "Firebase logging disabled - initialization failed",
                    {"error": str(e)}
                )
            self._enabled = False

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not self._initialized:
            try:
                # Initialize Firebase app if not already done
                if not firebase_admin._apps:
                    cred = credentials.Certificate(self.service_account_path)
                    firebase_admin.initialize_app(cred, {"projectId": self.project_id})
                
                # Initialize Firestore client
                self._firestore_client = firestore.client()
                
                # Initialize Storage client
                self._storage_client = storage.bucket()
                
                self._initialized = True
                
            except Exception as e:
                self.logger.error("Firebase initialization failed", {"error": str(e)})
                raise

    def is_enabled(self) -> bool:
        """Check if Firebase logging is enabled"""
        return self._enabled and self._initialized

    async def log_entry(
        self,
        level,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an entry to Firebase Firestore

        Args:
            level: Log level
            message: Log message
            context: Additional context data

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            # Create log document
            log_doc = {
                "timestamp": datetime.now().isoformat(),
                "level": level.value.upper(),
                "environment": get_environment().upper(),
                "message": message,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            
            if context is not None:
                if not isinstance(context, dict):
                    context = {"context": str(context)}
                log_doc["context"] = context

            # Add to Firestore
            collection_ref = self._firestore_client.collection("logs")
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: collection_ref.add(log_doc)
            )
            
            return True

        except Exception as e:
            self.logger.error(
                "Failed to log to Firebase",
                {"error": str(e), "message": message}
            )
            return False

    async def upload_log_file(self, log_file_path: str) -> bool:
        """
        Upload a log file to Firebase Storage

        Args:
            log_file_path: Path to the log file to upload

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            # Check if file exists
            if not os.path.exists(log_file_path):
                self.logger.warning(f"Log file not found: {log_file_path}")
                return False

            # Generate storage path with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(log_file_path)
            storage_path = f"logs/{timestamp}_{filename}"

            # Upload to Firebase Storage
            blob = self._storage_client.blob(storage_path)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: blob.upload_from_filename(log_file_path)
            )

            self.logger.info(
                "Log file uploaded to Firebase Storage",
                {"file": filename, "storage_path": storage_path}
            )
            
            return True

        except Exception as e:
            self.logger.error(
                "Failed to upload log file to Firebase Storage",
                {"error": str(e), "file": log_file_path}
            )
            return False

    async def cleanup_old_logs(self, days_to_keep: int = 30) -> bool:
        """
        Clean up old log entries from Firestore

        Args:
            days_to_keep: Number of days to keep logs

        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False

        try:
            # Calculate cutoff date
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)

            # Query for old logs
            collection_ref = self._firestore_client.collection("logs")
            old_logs = collection_ref.where("created_at", "<", cutoff_date).stream()

            # Delete old logs
            deleted_count = 0
            for doc in old_logs:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: doc.reference.delete()
                )
                deleted_count += 1

            if deleted_count > 0:
                self.logger.info(
                    f"Cleaned up {deleted_count} old log entries from Firebase"
                )

            return True

        except Exception as e:
            self.logger.error(
                "Failed to cleanup old logs from Firebase",
                {"error": str(e)}
            )
            return False 