---
id: password-hashing
title: "Password Hashing"
tier: 2
triggers: [password, hash, bcrypt, argon2]
summary: "Argon2/bcrypt with per-user salt; never roll your own; rehash on cost bump."
---

# Password Hashing

Argon2/bcrypt with per-user salt; never roll your own; rehash on cost bump.

## When this applies
Loads when the prompt mentions: password, hash, bcrypt, argon2.

## Guidance
- Argon2/bcrypt with per-user salt; never roll your own; rehash on cost bump.
- Make the safe choice the default; document the exception when you deviate.
- Prefer the boring, well-understood option over the clever one.
