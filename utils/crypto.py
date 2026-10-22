from passlib.context import CryptContext

# bcrypt for every stored password; passlib flags hashes needing an upgrade on verify.
pwd_context = CryptContext(schemes=("bcrypt",), deprecated="auto")
