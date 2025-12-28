# RAM-CLI Complete Guide
> i used ai to generate this

## Table of Contents
1. [First Run & Crypto Setup](#crypto-setup)
2. [Account Management](#account-management)
3. [Raw API Commands](#raw-api)
4. [Script System](#script-system)
5. [Configuration](#configuration)

---

## Crypto Setup

On first run, you'll enter **CRYPTO MODE** where you must manually configure encryption at the assembly level.

### Hardware Encryption Setup

```bash
crypto> cipher --init aes
+ initialized cipher context

crypto> cipher --set-mode gcm
+ mode: GCM

crypto> cipher --set-key-size 256
+ key size: 256 bits

crypto> kdf --init hardware
+ initialized hardware KDF

crypto> kdf --get-hwid csproduct-uuid
12345678-ABCD-EFGH...

crypto> kdf --get-hwid cpu-processorid
BFEBFBFF000906EA

crypto> kdf --derive-key
+ key derived from hardware

crypto> cipher --load-key
+ key loaded

crypto> cipher --test
+ encryption test: PASS

crypto> config --set-method hardware
crypto> config --set-cipher aes-256-gcm
crypto> config --commit
+ configuration saved
```

### Password Encryption Setup

```bash
crypto> cipher --init aes
crypto> cipher --set-mode gcm
crypto> cipher --set-key-size 256

crypto> kdf --init pbkdf2
+ initialized PBKDF2

crypto> kdf --set-hash sha256
+ hash: SHA256

crypto> kdf --set-iterations 100000
+ iterations: 100000

crypto> kdf --generate-salt
bXktc2FsdC12YWx1ZQ==

crypto> kdf --set-salt bXktc2FsdC12YWx1ZQ==
+ salt configured

crypto> kdf --derive-key mypassword
+ key derived

crypto> cipher --load-key
crypto> cipher --test

crypto> config --set-method password
crypto> config --set-kdf pbkdf2
crypto> config --set-cipher aes-256-gcm
crypto> config --commit
```

### No Encryption
if u use this ur not cool

```bash
crypto> config --set-method none
crypto> config --commit
```

---

## Account Management

### Add Account
```bash
[1] > add
# Opens browser for login

[1] > add 3
# Add 3 accounts

[1] > add 1 https://roblox.com/login
# Custom URL
```

### List Accounts
```bash
[1] > ls
USER                      COOKIE                    NOTE
----------------------------------------------------------------------
myuser                    .ROBLOSECURITY=abc...     my main
```

### Delete Account
```bash
[1] > rm myuser
+ deleted: myuser
```

### Get/Set Data
```bash
[1] > get myuser cookie
.ROBLOSECURITY=abc123...

[1] > set myuser note "my alt account"
+ set

[1] > note myuser
my alt account

[1] > note myuser "new note"
+ updated
```

---

## API Commands

### Get Auth Ticket
```bash
[1] > api --auth myuser
POST auth.roblox.com/v1/authentication-ticket

AUTH_TICKET:
abc123xyz...
```

### Build Launch URL
```bash
[1] > api --launch <place_id> <auth_ticket> [ps_code] [job_id]

# Skip parameters with -
[1] > api --launch 123456 ticket123 - job-id-here
```

### Execute Launch URL
```bash
[1] > exec roblox-player:1+launchmode:play+gameinfo:...
+ Roblox launched
```

### Other API Commands
```bash
[1] > api --csrf myuser
[1] > api --user <cookie>
[1] > api --uid <username>
[1] > api --presence myuser 123456
[1] > api --validate myuser
[1] > api --game 123456
```

---

## Script System (Mod Support)

### Example Script
```bash
[1] > scriptedit autolaunch
1> api --auth {0}
2> api --launch {1} {auth_ticket}
3> exec {url}
4> done
+ saved script 'autolaunch' with 3 commands
```

### Run Script
```bash
[1] > script autolaunch myuser 123456789
> api --auth myuser
+ captured: auth_ticket
> api --launch 123456789 <ticket>
+ captured: url
> exec roblox-player:...
+ Roblox launched
```

### Variables
- `{0}`, `{1}`, `{2}` - Script arguments
- `{auth_ticket}` - Auto-captured from `api --auth`
- `{url}` - Auto-captured from `api --launch`

### Manage Scripts
```bash
[1] > script
# List all scripts

[1] > scriptdel autolaunch
# Delete script
```

---

## Configuration

### View Config
```bash
[1] > cfg list
[1] > cfg list detection
[1] > cfg get detection.method
```

### Set Config
```bash
[1] > cfg set detection.method url
[1] > cfg set detection.custom_script "console.log('test')"
```

### Reset Config
```bash
[1] > cfg reset
```

### Aliases
```bash
[1] > alias list
[1] > alias add l "ls"
[1] > alias rm l
```

---

## Tips

- Use `-` to skip optional parameters
- Type `help` for command list
- Type `q` to quit
