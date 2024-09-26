# app/core/services/session_manager.py
from __future__ import annotations

import time

class SessionManager:
    def __init__(self, session_timeout: int):
        """
        Initializes the session manager with a session timeout.

        :param session_timeout: Time in seconds before a session expires due to inactivity
        """
        self.session_timeout = session_timeout
        self.sessions: dict[str, dict] = {}  # A dictionary to store sessions, mapping session IDs to session data

    def create_session(self, user_id: str) -> str:
        """
        Creates a new session for the given user.

        :param user_id: The ID of the user
        :return: The session ID
        """
        session_id = f"session_{user_id}_{int(time.time())}"  # Generate a unique session ID
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_active': time.time(),
        }
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """
        Validates whether the session is still active.

        :param session_id: The session ID
        :return: True if the session is valid, False if it is expired or invalid
        """
        session = self.sessions.get(session_id)
        if session is None:
            return False

        # Check if session is expired
        if time.time() - session['last_active'] > self.session_timeout:
            self.revoke_session(session_id)
            return False

        # Update last active timestamp
        session['last_active'] = time.time()
        return True

    def revoke_session(self, session_id: str) -> None:
        """
        Revokes a session (logs out the user).

        :param session_id: The session ID
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def is_session_active(self, session_id: str) -> bool:
        """
        Check if the session is still active.

        :param session_id: The session ID
        :return: True if the session is active, False otherwise
        """
        return session_id in self.sessions and self.validate_session(session_id)
