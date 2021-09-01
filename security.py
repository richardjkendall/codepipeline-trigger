from functools import wraps
import logging
import base64
import hmac
import hashlib
import re
from botocore.retries import base
from flask import request

from error_handler import AccessDeniedException

logger = logging.getLogger(__name__)

def to_bytes(input):
  if isinstance(input, (bytes, bytearray)):
    return input
  else:
    return bytes(input, "utf-8")

def check_hmac(http_header_name, token):
  """
  Decorator for checking hmac signature
  """
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      """
      check for signature in headers and verify it if found
      """
      if http_header_name in request.headers:
        signature = request.headers[http_header_name]
        if signature is None:
          logger.info("Header was found, but empty")
          raise AccessDeniedException("Denied.")
        logger.info(f"Signature in request is {signature}")
        sha_name, sig = signature.split("=", 1)
        if sha_name != "sha256":
          logger.info(f"Expected sha256, but found {sha_name}")
        request_body = request.get_data()
        request_body_type = type(request_body)
        logger.info(f"Type of request body {request_body_type}")
        logger.info(f"Request body is {request_body}")
        mac = hmac.new(
          key=bytes(token, "utf-8"),
          msg=to_bytes(request_body),
          digestmod=hashlib.sha256
        )
        mac_b64 = base64.b64encode(mac.digest()).decode()
        if not hmac.compare_digest(bytes(mac_b64, "utf-8"), bytes(sig, "utf-8")):
          logger.info("Signatures did not match")
          raise AccessDeniedException("Denied.")
        else:
          logger.info("Signature matched, yay!")
          return f(*args, **kwargs)
      else:
        logger.info(f"{http_header_name} header is missing")
        raise AccessDeniedException("Expected header is missing")
    return decorated_function
  return decorator

def secured(username, password):
  """
  Decorator for checking for basic auth which matches what we need
  """
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      """
      check for basic auth header
      """
      if "Authorization" in request.headers or "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.startswith("Basic"):
          decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
          decoded_bits = decoded.split(":")
          provided_username = decoded_bits[0]
          provided_password = decoded_bits[1]
          if provided_username == username and provided_password == password:
            logger.info("Username/password match")
            return f(*args, **kwargs)
          else:
            logger.info("Username/password mismatch")
            raise AccessDeniedException("Username/password is mismatched")
        else:
          logger.info("We only support basic authentication")
          raise AccessDeniedException("Only basic authentication is supported")
      else:
        logger.info("Authorization header is missing")
        raise AccessDeniedException("Header is missing")
    return decorated_function
  return decorator