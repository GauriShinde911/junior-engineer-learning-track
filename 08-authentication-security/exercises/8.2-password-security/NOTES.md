# 8.2 Password Security — Concepts & Reference

## Core Concepts
Authentication relies on verifying that users know a secret without the application ever storing or knowing that secret itself. Modern password security mandates slow, salted, one-way cryptographic hashes that resist offline brute-force attacks even if the database is leaked.

## Hashing vs. Encryption
- **Hashing is One-Way**: A cryptographic hash function maps arbitrary text to a fixed-size digest irreversibly. You cannot "decrypt" a hash back to the password; verification is performed by hashing candidate input and comparing digests.
- **Encryption is Two-Way**: Encryption transforms plaintext into ciphertext with a reversible key. Passwords must never be encrypted—if an attacker steals the encryption key, every user credential is compromised.

## Salting & Cost Factors
- **Salting**: Appending a unique, cryptographically random string (the salt) to each password before hashing. This ensures two users with identical passwords yield completely different hashes, neutralizing precomputed rainbow table attacks.
- **Cost Factor (Work Factor)**: General hash functions like MD5 or SHA-256 are engineered for speed (e.g., integrity checks), enabling attackers to test billions of guesses per second on GPUs. In contrast, `bcrypt` includes an adjustable cost factor (rounds) that intentionally consumes CPU cycles and memory, slowing brute-force attempts to a crawl while remaining imperceptible to legitimate users during login.

## Key Functions Used
- `bcrypt.gensalt(rounds=12)`: Generates a cryptographically random salt and embeds the cost factor.
- `bcrypt.hashpw(password, salt)`: Computes the salted bcrypt hash digest (containing algorithm, cost, salt, and hash).
- `bcrypt.checkpw(candidate, stored_hash)`: Securely checks credentials using constant-time comparison to prevent timing side-channels.

## Applied Implementation in this Folder
In [`user_store.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/08-authentication-security/exercises/8.2-password-security/user_store.py), the `UserStore` class manages user registration and authentication exclusively via bcrypt hashes. Plaintext passwords are validated in memory and discarded immediately, ensuring only salted digests are persisted.
