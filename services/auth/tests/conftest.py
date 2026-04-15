import os

# Must be set before importing security module which validates it at import time
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars!")
