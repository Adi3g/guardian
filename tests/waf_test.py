# tests/test_waf.py
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.services.waf import WAF

def test_waf_blocks_sql_injection():
    waf_config = {
        'enabled': True,
        'rules': [
            {'name': 'Block SQL Injection', 'pattern': 'SELECT|UPDATE|DELETE|INSERT|DROP|ALTER', 'action': 'block'},
        ],
    }
    waf = WAF(waf_config)

    # This content simulates an SQL injection attack
    request_content = "SELECT * FROM users WHERE username='admin'"

    with pytest.raises(HTTPException) as excinfo:
        waf.inspect_request(request_content)

    assert excinfo.value.status_code == 403
    assert 'Blocked by WAF rule: Block SQL Injection' in str(excinfo.value.detail)

def test_waf_allows_safe_request():
    waf_config = {
        'enabled': True,
        'rules': [
            {'name': 'Block SQL Injection', 'pattern': 'SELECT|UPDATE|DELETE|INSERT|DROP|ALTER', 'action': 'block'},
        ],
    }
    waf = WAF(waf_config)

    # This content is a safe, non-malicious request
    request_content = 'GET /home HTTP/1.1'

    # Ensure the WAF does not raise an exception for a safe request
    waf.inspect_request(request_content)

def test_waf_blocks_xss():
    waf_config = {
        'enabled': True,
        'rules': [
            {'name': 'Block XSS', 'pattern': '<script>|<iframe>|onerror|onload', 'action': 'block'},
        ],
    }
    waf = WAF(waf_config)

    # This content simulates a cross-site scripting (XSS) attack
    request_content = "<script>alert('xss')</script>"

    with pytest.raises(HTTPException) as excinfo:
        waf.inspect_request(request_content)

    assert excinfo.value.status_code == 403
    assert 'Blocked by WAF rule: Block XSS' in str(excinfo.value.detail)
