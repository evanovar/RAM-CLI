# RAM-CLI Encryption Wiki

This document explains **what** each command actually does.
> i used AI to generate this wiki

---

## Table of Contents
1. [Why So Many Commands?](#why-so-many-commands)
2. [Encryption Methods](#encryption-methods)
3. [Command Breakdown](#command-breakdown)
4. [Minimal Setups](#minimal-setups)

---

## Why So Many Commands?

In most applications, encryption setup is hidden behind a simple "Choose Password" dialog. RAM-CLI exposes **every step** of the cryptographic process, forcing you to manually configure:

1. **Cipher** - The encryption algorithm (AES)
2. **Mode** - How the cipher operates (GCM)
3. **Key Derivation** - How to generate encryption keys (PBKDF2 or Hardware)
4. **Configuration** - Saving your choices

---

## Encryption Methods

### 1. Hardware Encryption
- **Locks to your PC** - Accounts can only be decrypted on this machine
- **Uses hardware IDs** - CPU, motherboard, etc.
- **No password needed** - Automatic unlock on your PC
- **Can't transfer** - Moving to new PC requires re-adding accounts

### 2. Password Encryption
- **Portable** - Works on any machine
- **Password protected** - Must enter password each time
- **Transferable** - Can copy data to another PC
- **Secure** - Uses PBKDF2 with 100,000 iterations

### 3. No Encryption
- **Plain text** - Accounts stored unencrypted
- **Fast** - No crypto overhead
- **Insecure** - Anyone can read your cookies
- **Quick setup** - Just 2 commands

---

## Command Breakdown

### Cipher Commands

#### `cipher --init aes`
**What it does:** Initializes the AES (Advanced Encryption Standard) cipher context.

**Why:** AES is the industry-standard encryption algorithm. This tells the system "I want to use AES for encryption."

**Technical:** Creates a cipher object that will later encrypt/decrypt your account data.

---

#### `cipher --set-mode gcm`
**What it does:** Sets the cipher mode to GCM (Galois/Counter Mode).

**Why:** GCM provides both encryption AND authentication, preventing tampering.

**Technical:** GCM is an AEAD (Authenticated Encryption with Associated Data) mode that's faster and more secure than older modes like CBC.

---

#### `cipher --set-key-size 256`
**What it does:** Sets the encryption key size to 256 bits.

**Why:** Larger keys = stronger encryption. 256-bit AES is military-grade.

**Technical:** AES supports 128, 192, or 256-bit keys. 256 is the strongest.

---

#### `cipher --set-block-size 16`
**What it does:** Sets the block size to 16 bytes (128 bits).

**Why:** AES always uses 16-byte blocks regardless of key size.

**Technical:** This is mostly for completeness - AES block size is always 128 bits.

---

#### `cipher --load-key`
**What it does:** Loads the derived key into the cipher context.

**Why:** The cipher needs a key to encrypt/decrypt. This connects your derived key to the cipher.

**Technical:** Transfers the key from KDF output to the cipher's key schedule.

---

#### `cipher --test`
**What it does:** Tests encryption and decryption with the current key.

**Why:** Verifies everything is configured correctly before saving.

**Technical:** Encrypts "test_encryption" bytes, then decrypts and verifies the result matches.

---

### KDF Commands (Key Derivation Function)

#### `kdf --init pbkdf2`
**What it does:** Initializes PBKDF2 (Password-Based Key Derivation Function 2).

**Why:** Converts a password into a strong encryption key.

**Technical:** PBKDF2 applies a hash function thousands of times to make brute-force attacks impractical.

---

#### `kdf --init hardware`
**What it does:** Initializes hardware-based key derivation.

**Why:** Uses your PC's unique hardware IDs to generate a key.

**Technical:** Combines CPU ID, motherboard serial, etc. into a machine-specific key.

---

#### `kdf --set-hash sha256`
**What it does:** Sets the hash function to SHA-256.

**Why:** SHA-256 is cryptographically secure and widely trusted.

**Technical:** PBKDF2 uses this hash function internally for key stretching.

---

#### `kdf --set-iterations 100000`
**What it does:** Sets PBKDF2 to run 100,000 iterations.

**Why:** More iterations = slower brute-force attacks. 100k is the recommended minimum.

**Technical:** Each iteration applies SHA-256, making password cracking exponentially harder.

---

#### `kdf --generate-salt`
**What it does:** Generates a random 32-byte salt.

**Why:** Salts prevent rainbow table attacks and ensure unique keys even with the same password.

**Technical:** Uses cryptographically secure random number generator (CSRNG).

**Output:** Base64-encoded random bytes (e.g., `bXktc2FsdC12YWx1ZQ==`)

---

#### `kdf --set-salt <base64>`
**What it does:** Manually sets the salt value.

**Why:** Allows you to use a specific salt (for recovery or testing).

**Technical:** Decodes base64 and stores as the salt for key derivation.

---

#### `kdf --get-hwid <component>`
**What it does:** Retrieves hardware identifier from your PC.

**Why:** Needed for hardware-based encryption.

**Components:**
- `csproduct-uuid` - Motherboard UUID
- `cpu-processorid` - CPU serial number
- `baseboard-serial` - Motherboard serial

**Technical:** Uses Windows `wmic` commands to query hardware info.

---

#### `kdf --derive-key <password>`
**What it does:** Derives a 32-byte encryption key from your password and salt.

**Why:** This is the actual key that will encrypt your accounts.

**Technical:** Runs PBKDF2(password, salt, iterations=100000, dkLen=32) to produce the key.

**For hardware:** Derives key from hardware IDs instead of password.

---

### Config Commands

#### `config --set-method <hardware|password|none>`
**What it does:** Declares which encryption method you're using.

**Why:** Tells the system how to decrypt accounts on next startup.

**Technical:** Saves to `encryption_config.json` so the CLI knows what to do.

---

#### `config --set-cipher <spec>`
**What it does:** Records the cipher specification.

**Why:** Documents what cipher you configured (for reference).

**Technical:** Informational only - doesn't affect actual encryption.

---

#### `config --set-kdf <spec>`
**What it does:** Records the KDF specification.

**Why:** Documents what KDF you configured (for reference).

**Technical:** Informational only - doesn't affect actual key derivation.

---

#### `config --commit`
**What it does:** Saves all configuration to disk and enables encryption.

**Why:** Finalizes setup and creates `encryption_config.json`.

**Technical:** Calls `enable_hardware_encryption()`, `enable_password_encryption()`, or `enable_no_encryption()` based on method.

---

## Minimal Setups

### Fastest: No Encryption (2 commands)
```bash
crypto> config --set-method none
crypto> config --commit
```

### Hardware Encryption (Minimal - 7 commands)
```bash
crypto> cipher --init aes
crypto> kdf --init hardware
crypto> kdf --get-hwid csproduct-uuid
crypto> kdf --derive-key
crypto> config --set-method hardware
crypto> config --commit
crypto> q
```

### Password Encryption (Minimal - 9 commands)
```bash
crypto> cipher --init aes
crypto> kdf --init pbkdf2
crypto> kdf --generate-salt
crypto> kdf --set-salt <paste_salt_here>
crypto> kdf --derive-key mypassword
crypto> config --set-method password
crypto> config --commit
crypto> q
```
