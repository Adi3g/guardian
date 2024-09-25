# app/core/services/waf.py
from __future__ import annotations

import re

from fastapi import HTTPException

class WAF:
    """
    Web Application Firewall (WAF) class that checks incoming requests
    against predefined patterns and blocks malicious traffic.
    """

    def __init__(self, waf_config):
        """
        Initializes the WAF with rules from the configuration.

        :param waf_config: WAF configuration containing rules and patterns
        """
        self.enabled = waf_config.get('enabled', False)
        self.rules = waf_config.get('rules', [])

    def inspect_request(self, request_content: str):
        """
        Inspects incoming request content and checks it against WAF rules.

        :param request_content: The content of the incoming request (e.g., URL, headers, body)
        :raises HTTPException: If malicious content is detected
        """
        if not self.enabled:
            return

        for rule in self.rules:
            pattern = rule.get('pattern', '')
            if re.search(pattern, request_content, re.IGNORECASE):
                raise HTTPException(status_code=403, detail=f"Blocked by WAF rule: {rule['name']}")
