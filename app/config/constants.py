"""
Application-wide constants.
"""

# OTP purpose keys — used as Redis key namespaces and rate-limit scopes
OTP_PURPOSE_SIGNUP = "signup"
OTP_PURPOSE_LOGIN = "login"
OTP_PURPOSE_PASSWORD_RESET = "reset_password"
