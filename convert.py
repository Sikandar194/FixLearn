import hashlib
password = "test"
print(hashlib.sha256(password.encode()).hexdigest())






