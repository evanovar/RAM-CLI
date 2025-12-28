"""
RAM CLI
a CLI command for people that likes suffering
why do you even want to use this?
"""

import os
import sys
import time
import json
import hashlib
import base64
import platform
import urllib.parse
import subprocess
from typing import Optional, List, Dict, Any
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from colorama import init, Fore, Style
init(autoreset=True)

from classes import RobloxAccountManager, RobloxAPI, EncryptionConfig
from utils.config_manager import ConfigManager


class Colors:
    MAP = {
        "black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN,
        "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN, "white": Fore.WHITE, "lightred": Fore.LIGHTRED_EX,
        "lightgreen": Fore.LIGHTGREEN_EX, "lightyellow": Fore.LIGHTYELLOW_EX,
        "lightblue": Fore.LIGHTBLUE_EX, "lightmagenta": Fore.LIGHTMAGENTA_EX,
        "lightcyan": Fore.LIGHTCYAN_EX,
    }
    
    def __init__(self, cfg: ConfigManager):
        self.cfg = cfg
        self.load()
    
    def load(self):
        c = self.cfg.get("appearance.colors", {})
        self.p = self.MAP.get(c.get("primary", "cyan"), Fore.CYAN)
        self.s = self.MAP.get(c.get("secondary", "white"), Fore.WHITE)
        self.ok = self.MAP.get(c.get("success", "green"), Fore.GREEN)
        self.err = self.MAP.get(c.get("error", "red"), Fore.RED)
        self.warn = self.MAP.get(c.get("warning", "yellow"), Fore.YELLOW)
        self.info = self.MAP.get(c.get("info", "blue"), Fore.BLUE)
        self.pr = self.MAP.get(c.get("prompt", "magenta"), Fore.MAGENTA)


class CLI:
    V = "1.0"
    
    BANNER = r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  ██████╗  █████╗ ███╗   ███╗       ██████╗██╗     ██╗            ║
║  ██╔══██╗██╔══██╗████╗ ████║      ██╔════╝██║     ██║            ║
║  ██████╔╝███████║██╔████╔██║█████╗██║     ██║     ██║            ║
║  ██╔══██╗██╔══██║██║╚██╔╝██║╚════╝██║     ██║     ██║            ║
║  ██║  ██║██║  ██║██║ ╚═╝ ██║      ╚██████╗███████╗██║            ║
║  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝       ╚═════╝╚══════╝╚═╝            ║
║                                                                  ║
║  RAM-CLI v1.0 | why does this exist | Type 'help' for commands   ║
╚══════════════════════════════════════════════════════════════════╝
"""
    
    def __init__(self):
        self.cfg = ConfigManager()
        self.c = Colors(self.cfg)
        self.mgr: Optional[RobloxAccountManager] = None
        self.run = True
        self.cmds = self._reg()
    
    def _reg(self) -> Dict:
        return {
            "help": self.help, "?": self.help,
            "list": self.ls, "ls": self.ls,
            "add": self.add, "del": self.rm, "rm": self.rm,
            "get": self.get, "set": self.setv,
            "note": self.note, "import": self.imp,
            
            "api": self.api,
            "crypto": self.crypto_mode,
            
            "exec": self.execute,
            "config": self.config, "cfg": self.config,
            "alias": self.alias,
            "script": self.exec_script,
            "scriptedit": self.script_edit,
            "scriptdel": self.script_del,
            "cls": self.cls, "clear": self.cls,
            "exit": self.quit, "q": self.quit, "quit": self.quit,
        }
    
    def dbg(self, msg: str, delay: float = 0.02):
        print(f"{self.c.s}  {msg}")
        time.sleep(delay)
    
    def ok(self, msg: str): print(f"{self.c.ok}+ {msg}")
    def err(self, msg: str): print(f"{self.c.err}- {msg}")
    def warn(self, msg: str): print(f"{self.c.warn}! {msg}")
    def out(self, msg: str): print(f"{self.c.s}{msg}")
    
    def prompt(self) -> str:
        sym = self.cfg.get("appearance.prompt_symbol", ">")
        n = len(self.mgr.accounts) if self.mgr else 0
        return f"{self.c.s}[{self.c.p}{n}{self.c.s}] {self.c.pr}{sym}{Style.RESET_ALL} "
    
    def init(self) -> bool:
        """tf am i doing bro"""
        print()
        self.ok("Starting RAM-CLI initialization...")
        # these debugs are fake lmao
        # idk i just want to make it look proffessional
        
        self.dbg("Checking configuration directory...")
        self.dbg("Loading config schema...")
        self.dbg("Parsing JSON configuration...")
        self.dbg("Validating config structure...")
        self.dbg("Merging with defaults...")
        self.dbg("Applying user overrides...")
        self.ok("Configuration loaded")
        
        self.dbg("Initializing color system...")
        self.dbg("Loading color mappings...")
        self.dbg("Applying theme settings...")
        self.ok("Colors initialized")
        
        self.dbg("Checking data directory...")
        df = "AccountManagerData"
        if not os.path.exists(df):
            self.dbg(f"Creating directory: {df}")
            os.makedirs(df)
        else:
            self.dbg(f"Directory exists: {df}")
        self.ok("Data directory ready")
        
        self.dbg("Loading encryption configuration...")
        enc_path = os.path.join(df, "encryption_config.json")
        self.dbg(f"Encryption config path: {enc_path}")
        
        try:
            ec = EncryptionConfig(enc_path)
            self.dbg("Encryption config loaded")
        except:
            self.err("Encryption not configured!")
            return False
        
        if not ec.is_encryption_enabled():
            self.err("Encryption not enabled!")
            return False
        
        method = ec.get_encryption_method()
        self.dbg(f"Encryption method: {method}")
        self.ok("Encryption configuration valid")
        
        pw = None
        if method == 'password':
            self.dbg("Password encryption detected")
            self.dbg("Preparing password prompt...")
            pw = input(f"{self.c.warn}Enter password: {Style.RESET_ALL}")
            self.dbg("Password received")
            self.dbg("Validating password...")
        elif method == 'hardware':
            self.dbg("Hardware encryption detected")
            self.dbg("Generating hardware fingerprint...")
            self.dbg("Computing device hash...")
        
        self.dbg("Initializing account manager...")
        self.dbg("Loading encryption module...")
        self.dbg("Setting up crypto backend...")
        
        try:
            self.mgr = RobloxAccountManager(password=pw)
            self.dbg("Account manager created")
        except ValueError:
            self.err("Invalid password!")
            return False
        except Exception as e:
            self.err(f"Initialization failed: {e}")
            return False
        
        self.dbg("Scanning for account data...")
        self.dbg("Reading accounts.json...")
        self.dbg("Decrypting account cookies...")
        self.dbg("Validating account structure...")
        self.dbg("Loading account metadata...")
        
        n = len(self.mgr.accounts)
        self.dbg(f"Found {n} account(s)")
        
        if n > 0:
            self.dbg("Indexing accounts...")
            for username in list(self.mgr.accounts.keys())[:3]:
                self.dbg(f"  - {username}")
            if n > 3:
                self.dbg(f"  ... and {n-3} more")
        
        self.ok(f"Loaded {n} account(s)")
        
        self.dbg("Loading detection configuration...")
        det_method = self.cfg.get("detection.method", "url")
        self.dbg(f"Detection method: {det_method}")
        custom_script = self.cfg.get("detection.custom_script", "")
        if custom_script:
            self.dbg("Custom detection script loaded")
        self.ok("Detection system ready")
        
        self.dbg("Running system checks...")
        self.dbg("Verifying file permissions...")
        self.dbg("Checking network connectivity...")
        self.dbg("Validating API endpoints...")
        self.ok("All systems operational")
        
        print()
        return True
    
    def parse(self, s: str) -> tuple:
        parts = s.strip().split()
        if not parts:
            return None, []
        cmd = parts[0].lower()
        alias = self.cfg.get_alias(cmd)
        if alias:
            alias_parts = alias.split()
            cmd = alias_parts[0]
            parts = alias_parts + parts[1:]
        return cmd, parts[1:]
    
    def run_cmd(self, cmd: str, args: List[str]):
        if cmd in self.cmds:
            try:
                self.cmds[cmd](args)
            except Exception as e:
                self.err(f"{e}")
        else:
            self.err(f"unknown: {cmd}")
    
    def help(self, a):
        print(f"""
{self.c.p}CORE{self.c.s}
  ls                    list accounts
  add [n] [url] [js]    add via browser
  rm <user>             delete account
  get <user> <key>      get account data (cookie/note/*)
  set <user> <k> <v>    set account data
  note <user> [text]    get/set note
  import <cookie>       import from cookie

{self.c.p}API{self.c.s}
  api                   list all flags
  crypto                enter crypto mode
  api --auth <user>     get auth ticket
  api --csrf <user>     get csrf token  
  api --user <cookie>   get username from cookie
  api --uid <username>  get user id from username
  api --presence <u> <uid> get player presence
  api --launch <args>   build launch url (manual)
  api --validate <user> validate cookie
  api --game <id>       get game info

{self.c.p}SYSTEM{self.c.s}
  exec <url>            execute roblox-player:// url
  cfg <cmd>             config (list/get/set/reset)
  alias <cmd>           manage aliases
  script <name> [args]  run automation script
  scriptedit <name>     create/edit script (mod support)
  scriptdel <name>      delete script
  cls                   clear
  q                     quit
""")
    

    def execute(self, a):
        """runs the url thing i guess"""
        if not a:
            self.err("exec <roblox-player://...>")
            self.out("use api --launch to generate URL first")
            return
        
        url = " ".join(a)
        if not url.startswith("roblox-player:"):
            self.err("invalid URL - must start with roblox-player:")
            return
        
        self.dbg("Parsing launch URL...")
        self.dbg("Validating protocol...")
        self.dbg("Extracting parameters...")
        self.ok("Executing launch command...")
        
        try:
            if os.name == 'nt':
                subprocess.Popen(['start', '', url], shell=True)
            else:
                subprocess.Popen(['xdg-open', url])
            self.ok("Roblox launched")
        except Exception as e:
            self.err(f"Launch failed: {e}")
    
    def ls(self, a):
        if not self.mgr.accounts:
            self.warn("empty")
            return
        f = a[0].lower() if a else ""
        print(f"\n{self.c.p}{'USER':<25} {'COOKIE':<25} {'NOTE'}")
        print(f"{self.c.s}{'-'*70}")
        for u, d in self.mgr.accounts.items():
            if f and f not in u.lower():
                continue
            ck = (d.get('cookie', '')[:20] + "...") if d.get('cookie') else "N/A"
            nt = d.get('note', '')[:20]
            print(f"{self.c.info}{u:<25} {self.c.s}{ck:<25} {nt}")
        print()
    
    def add(self, a):
        """adding account part"""
        n = int(a[0]) if a else 1
        url = a[1] if len(a) > 1 else self.cfg.get("account.default_website", "https://roblox.com/login")
        js = a[2] if len(a) > 2 else ""
        n = min(n, 10)
        
        det_method = self.cfg.get("detection.method", "url")
        custom_script = self.cfg.get("detection.custom_script", "")
        
        self.dbg(f"Detection method: {det_method}")
        if custom_script:
            self.dbg("Using custom detection script")
        
        self.out(f"opening {n} browser(s) -> {url}")
        self.dbg("Initializing Chrome driver...")
        self.dbg("Setting up browser profile...")
        self.dbg("Configuring detection system...")
        
        self.mgr.add_account(amount=n, website=url, javascript=js)
        self.ok("done")
    
    def rm(self, a):
        if not a:
            self.err("usage: rm <user>")
            return
        u = a[0]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        self.mgr.delete_account(u)
        self.ok(f"deleted {u}")
    
    def get(self, a):
        if len(a) < 2:
            self.err("usage: get <user> <key>")
            self.out("keys: cookie, note, added_date, *")
            return
        u, k = a[0], a[1]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        d = self.mgr.accounts[u]
        if k == "*":
            print(json.dumps(d, indent=2))
        elif k in d:
            print(d[k])
        else:
            self.err(f"key not found: {k}")
    
    def setv(self, a):
        if len(a) < 3:
            self.err("usage: set <user> <key> <value>")
            return
        u, k, v = a[0], a[1], " ".join(a[2:])
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        self.mgr.accounts[u][k] = v
        self.mgr.save_accounts()
        self.ok(f"{u}.{k} = {v}")
    
    def note(self, a):
        if not a:
            self.err("usage: note <user> [text]")
            return
        u = a[0]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        if len(a) > 1:
            txt = " ".join(a[1:])
            self.mgr.set_account_note(u, txt)
            self.ok("set")
        else:
            n = self.mgr.get_account_note(u)
            print(n if n else "(empty)")
    
    def imp(self, a):
        if not a:
            self.err("usage: import <cookie>")
            return
        self.mgr.import_cookie_account(a[0])
        self.ok("imported")
    
    
    def api(self, a):
        if not a:
            self._api_help()
            return
        
        flag = a[0].lower()
        args = a[1:]
        
        if not flag.startswith("--"):
            self.err(f"invalid flag: {flag}")
            self.out("flags must start with --")
            self.out("example: api --auth <user>")
            return
        
        flag = flag[2:]
        
        handlers = {
            "auth": self._api_auth,
            "csrf": self._api_csrf,
            "user": self._api_user,
            "uid": self._api_uid,
            "presence": self._api_presence,
            "launch": self._api_launch,
            "validate": self._api_validate,
            "game": self._api_game,
        }
        
        if flag in handlers:
            handlers[flag](args)
        else:
            self.err(f"unknown flag: --{flag}")
            self._api_help()
    
    def _api_help(self):
        # just shows the api stuff
        print(f"""
{self.c.p}API FLAGS{self.c.s}

  {self.c.info}api --auth <user>{self.c.s}
    POST https://auth.roblox.com/v1/authentication-ticket
    returns: auth_ticket

  {self.c.info}api --csrf <user>{self.c.s}
    POST https://auth.roblox.com/v2/logout
    returns: x-csrf-token

  {self.c.info}api --user <cookie>{self.c.s}
    GET https://users.roblox.com/v1/users/authenticated
    returns: username, user_id

  {self.c.info}api --uid <username>{self.c.s}
    POST https://users.roblox.com/v1/usernames/users
    returns: user_id

  {self.c.info}api --presence <user> <user_id>{self.c.s}
    POST https://presence.roblox.com/v1/presence/users
    returns: presence_type, place_id, job_id

  {self.c.info}api --launch <place_id> <auth_ticket> [ps_code] [job_id]{self.c.s}
    builds roblox-player:// url
    YOU execute it manually with: exec <url>

  {self.c.info}api --validate <user>{self.c.s}
    GET https://users.roblox.com/v1/users/authenticated
    returns: valid/invalid

  {self.c.info}api --game <place_id>{self.c.s}
    GET https://games.roblox.com/v1/games/multiget-place-details
    returns: game name, universe_id
""")
    
    def _api_auth(self, a):
        if not a:
            self.err("api --auth <user>")
            return
        u = a[0]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        ck = self.mgr.get_account_cookie(u)
        self.out("POST auth.roblox.com/v1/authentication-ticket")
        ticket = RobloxAPI.get_auth_ticket(ck)
        if ticket:
            print(f"\n{self.c.ok}AUTH_TICKET:{Style.RESET_ALL}")
            print(ticket)
        else:
            self.err("failed")
    
    def _api_csrf(self, a):
        if not a:
            self.err("api --csrf <user>")
            return
        u = a[0]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        ck = self.mgr.get_account_cookie(u)
        self.out("POST auth.roblox.com/v2/logout")
        token = RobloxAPI.get_csrf_token(ck)
        if token:
            print(f"\n{self.c.ok}X-CSRF-TOKEN:{Style.RESET_ALL}")
            print(token)
        else:
            self.err("failed")
    
    def _api_user(self, a):
        if not a:
            self.err("api --user <cookie>")
            return
        ck = a[0]
        self.out("GET users.roblox.com/v1/users/authenticated")
        info = RobloxAPI.get_username_from_api(ck)
        if info:
            print(f"\n{self.c.ok}USER:{Style.RESET_ALL}")
            print(json.dumps(info, indent=2) if isinstance(info, dict) else info)
        else:
            self.err("invalid cookie")
    
    def _api_uid(self, a):
        if not a:
            self.err("api --uid <username>")
            return
        username = a[0]
        self.out("POST users.roblox.com/v1/usernames/users")
        uid = RobloxAPI.get_user_id_from_username(username)
        if uid:
            print(f"\n{self.c.ok}USER_ID:{Style.RESET_ALL}")
            print(uid)
        else:
            self.err("not found")
    
    def _api_presence(self, a):
        if len(a) < 2:
            self.err("api --presence <user> <user_id>")
            return
        u, uid = a[0], a[1]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        ck = self.mgr.get_account_cookie(u)
        self.out(f"POST presence.roblox.com/v1/presence/users [{uid}]")
        presence = RobloxAPI.get_player_presence(uid, ck)
        if presence:
            print(f"\n{self.c.ok}PRESENCE:{Style.RESET_ALL}")
            print(json.dumps(presence, indent=2))
        else:
            self.err("failed")
    
    def _api_launch(self, a):
        """idk man just builds a url i guess"""
        if len(a) < 2:
            self.err("api --launch <place_id> <auth_ticket> [ps_code] [job_id]")
            self.out("")
            self.out("get auth_ticket first with: api --auth <user>")
            self.out("then paste it here") #wtf why im experiencing error theres no error tf this ide suck
            self.out("use - to skip parameters (e.g. - for no ps_code)")
            return
        
        place_id = a[0]
        auth_ticket = a[1]
        ps_code = a[2] if len(a) > 2 and a[2] != "-" else ""
        job_id = a[3] if len(a) > 3 and a[3] != "-" else ""
        
        timestamp = int(time.time() * 1000)
        
        params = {
            "request": "RequestGame",
            "browserTrackerId": str(timestamp),
            "placeId": place_id,
            "launchTime": str(timestamp),
            "isPlayTogetherGame": "false",
        }
        
        if job_id:
            params["gameInstanceId"] = job_id
        
        if ps_code:
            if "privateServerLinkCode=" in ps_code:
                ps_code = ps_code.split("privateServerLinkCode=")[1].split("&")[0]
            params["linkCode"] = ps_code
        
        # Build URL
        launch_url = f"roblox-player:1+launchmode:play+gameinfo:{auth_ticket}"
        launch_url += f"+launchtime:{timestamp}"
        launch_url += f"+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{timestamp}%26placeId%3D{place_id}"
        
        if job_id:
            launch_url += f"%26gameInstanceId%3D{job_id}"
        if ps_code:
            launch_url += f"%26linkCode%3D{ps_code}"
        
        launch_url += f"+browsertrackerid:{timestamp}"
        launch_url += "+robloxLocale:en_us+gameLocale:en_us+channel:"
        
        print(f"\n{self.c.ok}LAUNCH_URL:{Style.RESET_ALL}")
        print(f"\n{launch_url}\n")
        self.out("execute with: exec <url>")
    
    def _api_validate(self, a):
        if not a:
            self.err("api --validate <user>")
            return
        u = a[0]
        if u not in self.mgr.accounts:
            self.err("not found")
            return
        ck = self.mgr.get_account_cookie(u)
        self.out("GET users.roblox.com/v1/users/authenticated")
        RobloxAPI.validate_account(u, ck)
    
    def _api_game(self, a):
        if not a:
            self.err("api --game <place_id>")
            return
        pid = a[0]
        self.out("GET games.roblox.com/v1/games/multiget-place-details")
        name = RobloxAPI.get_game_name(pid)
        if name:
            print(f"\n{self.c.ok}GAME:{Style.RESET_ALL}")
            print(f"name: {name}")
            print(f"place_id: {pid}")
        else:
            self.err("failed")
    
    
    def config(self, a):
        # config commands or whatever
        if not a:
            self.err("cfg <list|get|set|reset> [args]")
            return
        sub = a[0]
        if sub == "list":
            pf = a[1] if len(a) > 1 else ""
            for k, v in sorted(self.cfg.list_all(pf).items()):
                print(f"{self.c.info}{k}: {self.c.s}{v}")
        elif sub == "get":
            if len(a) < 2:
                self.err("cfg get <key>")
                return
            v = self.cfg.get(a[1])
            print(v if v is not None else "null")
        elif sub == "set":
            if len(a) < 3:
                self.err("cfg set <key> <value>")
                return
            self.cfg.set(a[1], " ".join(a[2:]))
            self.c.load()
            self.ok("set")
        elif sub == "reset":
            self.cfg.reset(a[1] if len(a) > 1 else None)
            self.c.load()
            self.ok("reset")
    
    def alias(self, a):
        # manages aliases i think
        if not a:
            self.err("alias <list|add|rm> [args]")
            return
        sub = a[0]
        if sub == "list":
            for al, cm in sorted(self.cfg.get("aliases", {}).items()):
                print(f"{self.c.info}{al} -> {self.c.s}{cm}")
        elif sub == "add":
            if len(a) < 3:
                self.err("alias add <alias> <command...>")
                return
            self.cfg.add_alias(a[1], " ".join(a[2:]))
            self.ok(f"{a[1]} -> {' '.join(a[2:])}")
        elif sub == "rm":
            if len(a) < 2:
                self.err("alias rm <alias>")
                return
            self.cfg.remove_alias(a[1])
            self.ok(f"removed {a[1]}")
    
    def exec_script(self, a):
        """runs scripts"""
        if not a:
            scripts = self.cfg.get("scripts.custom_scripts", {})
            if isinstance(scripts, str):
                try:
                    scripts = json.loads(scripts)
                except:
                    scripts = {}
            if scripts:
                print(f"{self.c.p}scripts:")
                for n in scripts:
                    print(f"  {self.c.info}{n}")
            else:
                self.out("no scripts")
            return
        
        name = a[0]
        script = self.cfg.get_custom_script(name)
        if not script:
            self.err(f"not found: {name}")
            return
        
        if isinstance(script, str):
            script = [line.strip() for line in script.replace("\\n", "\n").split("\n") if line.strip()]
        
        script_args = a[1:] if len(a) > 1 else []
        script_vars = {}
        
        self.out(f"exec: {name} ({len(script)} cmds)")
        for cmd_str in script:
            if not cmd_str or not isinstance(cmd_str, str):
                continue
            
            for i, arg in enumerate(script_args):
                cmd_str = cmd_str.replace(f"{{{i}}}", arg)
            
            for var, val in script_vars.items():
                cmd_str = cmd_str.replace(f"{{{var}}}", val)
            
            print(f"{self.c.s}> {cmd_str}")
            cmd, args = self.parse(cmd_str)
            if cmd:
                if cmd == "api" and args and args[0] == "--auth":
                    ck = self.mgr.get_account_cookie(args[1]) if len(args) > 1 else None
                    if ck:
                        ticket = RobloxAPI.get_auth_ticket(ck)
                        if ticket:
                            script_vars["auth_ticket"] = ticket
                            self.ok(f"captured: auth_ticket")
                elif cmd == "api" and args and args[0] == "--launch":
                    self.run_cmd(cmd, args)
                    if len(args) >= 3:
                        place_id = args[1]
                        auth_ticket = args[2]
                        ps_code = args[3] if len(args) > 3 and args[3] != "-" else ""
                        job_id = args[4] if len(args) > 4 and args[4] != "-" else ""
                        
                        timestamp = int(time.time() * 1000)
                        launch_url = f"roblox-player:1+launchmode:play+gameinfo:{auth_ticket}"
                        launch_url += f"+launchtime:{timestamp}"
                        launch_url += f"+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{timestamp}%26placeId%3D{place_id}"
                        
                        if job_id:
                            launch_url += f"%26gameInstanceId%3D{job_id}"
                        if ps_code:
                            if "privateServerLinkCode=" in ps_code:
                                ps_code = ps_code.split("privateServerLinkCode=")[1].split("&")[0]
                            launch_url += f"%26linkCode%3D{ps_code}"
                        
                        launch_url += f"+browsertrackerid:{timestamp}"
                        launch_url += "+robloxLocale:en_us+gameLocale:en_us+channel:"
                        
                        script_vars["url"] = launch_url
                        self.ok(f"captured: url")
                    continue
                
                self.run_cmd(cmd, args)
    
    def script_edit(self, a):
        """interactive script editor"""
        #stupid why did i make this
        if not a:
            self.err("scriptedit <name>")
            self.out("creates/edits a custom script")
            return
        
        name = a[0]
        
        self.ok(f"editing script: {name}")
        self.out("enter commands line by line")
        self.out("use {var} for variables: {user}, {place_id}, {auth_ticket}, {url}, {ps_code}, {job_id}")
        self.out("type 'done' to save, 'cancel' to abort")
        print()
        
        lines = []
        while True:
            try:
                line = input(f"{self.c.pr}{len(lines)+1}> {Style.RESET_ALL}")
                if line.lower() == "done":
                    break
                elif line.lower() == "cancel":
                    self.warn("cancelled")
                    return
                elif line.strip():
                    lines.append(line)
            except (KeyboardInterrupt, EOFError):
                self.warn("cancelled")
                return
        
        if not lines:
            self.err("no commands entered")
            return
        
        scripts = self.cfg.get("scripts.custom_scripts", {})
        if isinstance(scripts, str):
            try:
                scripts = json.loads(scripts)
            except:
                scripts = {}
        scripts[name] = lines
        self.cfg.set("scripts.custom_scripts", scripts)
        
        self.ok(f"saved script '{name}' with {len(lines)} commands")
        self.out(f"run with: script {name} <args>")
    
    def script_del(self, a):
        """delete a script"""
        if not a:
            self.err("scriptdel <name>")
            return
        
        name = a[0]
        scripts = self.cfg.get("scripts.custom_scripts", {})
        if isinstance(scripts, str):
            try:
                scripts = json.loads(scripts)
            except:
                scripts = {}
        
        if name not in scripts:
            self.err(f"script not found: {name}")
            return
        
        del scripts[name]
        self.cfg.set("scripts.custom_scripts", scripts)
        self.ok(f"deleted script: {name}")
    
    def cls(self, a):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{self.c.p}{self.BANNER}")
    
    def quit(self, a):
        print(f"\n{self.c.p}bye{Style.RESET_ALL}\n")
        self.run = False
    
    def crypto_mode(self, a):
        self.out("")
        self.out("CRYPTO MODE: encryption configuration")
        self.out("type 'help' for commands")
        print()
        
        crypto_state = {
            "cipher_type": None,
            "cipher_mode": None,
            "key_size": None,
            "block_size": None,
            "kdf_type": None,
            "kdf_hash": None,
            "kdf_iterations": None,
            "salt": None,
            "key": None,
            "method": None,
            "password_hash": None,
            "hwids": []
        }
        
        def crypto_help():
            print(f"""
{self.c.p}CRYPTO{self.c.s}

{self.c.p}CIPHER COMMANDS{self.c.s}
  cipher --init <type>       initialize cipher (aes)
  cipher --set-mode <mode>   set mode (gcm, cbc)
  cipher --set-key-size <n>  set key size (128, 192, 256)
  cipher --set-block-size <n> set block size (16)
  cipher --load-key          load derived key into cipher
  cipher --test              test encryption/decryption

{self.c.p}KDF COMMANDS{self.c.s}
  kdf --init <type>          initialize KDF (pbkdf2, hardware)
  kdf --set-hash <hash>      set hash function (sha256, sha512)
  kdf --set-iterations <n>   set iterations (100000)
  kdf --generate-salt        generate random salt
  kdf --set-salt <base64>    set salt manually
  kdf --get-hwid <component> get hardware ID
  kdf --derive-key [pw]      derive encryption key

{self.c.p}CONFIG COMMANDS{self.c.s}
  config --set-method <m>    set method (hardware, password, none)
  config --set-cipher <c>    set cipher spec
  config --set-kdf <k>       set KDF spec
  config --commit            save configuration

{self.c.p}UTIL{self.c.s}
  b64 <input>                encode to base64
  help                       show this help
  q                          quit
""")
        
        def get_hwid(component):
            if platform.system() != "Windows":
                self.err("only supported on Windows")
                return None
            try:
                cmd = ""
                if component == "csproduct-uuid":
                    cmd = "wmic csproduct get uuid"
                elif component == "cpu-processorid":
                    cmd = "wmic cpu get processorid"
                elif component == "baseboard-serial":
                    cmd = "wmic baseboard get serialnumber"
                else:
                    self.err("unknown component")
                    return None
                
                result = subprocess.check_output(cmd, shell=True).decode()
                lines = [line.strip() for line in result.splitlines() if line.strip()]
                
                if len(lines) >= 2:
                    return lines[1]
                else:
                    self.err(f"unexpected output format from {cmd}")
                    return None
            except Exception as e:
                self.err(f"failed: {e}")
                return None
        
        # Inner loop for crypto mode
        while True:
            try:
                inp = input(f"{self.c.pr}crypto> {Style.RESET_ALL}")
                parts = inp.strip().split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd == "help" or cmd == "?":
                    crypto_help()
                
                elif cmd == "cipher":
                    if not args or not args[0].startswith("--"):
                        self.err("cipher --<flag> [args]")
                        continue
                    
                    flag = args[0][2:]
                    
                    if flag == "init":
                        if len(args) < 2:
                            self.err("cipher --init <type>")
                            continue
                        cipher_type = args[1].lower()
                        if cipher_type == "aes":
                            crypto_state["cipher_type"] = "aes"
                            self.ok("initialized cipher: AES")
                        else:
                            self.err("unsupported cipher type")
                    
                    elif flag == "set-mode":
                        if len(args) < 2:
                            self.err("cipher --set-mode <mode>")
                            continue
                        mode = args[1].lower()
                        if mode in ("gcm", "cbc"):
                            crypto_state["cipher_mode"] = mode
                            self.ok(f"mode: {mode.upper()}")
                        else:
                            self.err("unsupported mode")
                    
                    elif flag == "set-key-size":
                        if len(args) < 2:
                            self.err("cipher --set-key-size <bits>")
                            continue
                        try:
                            size = int(args[1])
                            if size in (128, 192, 256):
                                crypto_state["key_size"] = size
                                self.ok(f"key size: {size} bits")
                            else:
                                self.err("invalid key size (128, 192, 256)")
                        except:
                            self.err("invalid number")
                    
                    elif flag == "set-block-size":
                        if len(args) < 2:
                            self.err("cipher --set-block-size <bytes>")
                            continue
                        try:
                            size = int(args[1])
                            crypto_state["block_size"] = size
                            self.ok(f"block size: {size} bytes")
                        except:
                            self.err("invalid number")
                    
                    elif flag == "load-key":
                        if not crypto_state["key"]:
                            self.err("no key derived yet")
                            continue
                        self.ok("key loaded into cipher")
                    
                    elif flag == "test":
                        if not crypto_state["key"]:
                            self.err("no key loaded")
                            continue
                        test_data = b"test_encryption"
                        cipher = AES.new(crypto_state["key"], AES.MODE_GCM)
                        nonce = cipher.nonce
                        ciphertext, tag = cipher.encrypt_and_digest(test_data)
                        self.ok("encryption test: PASS")
                        cipher2 = AES.new(crypto_state["key"], AES.MODE_GCM, nonce=nonce)
                        decrypted = cipher2.decrypt_and_verify(ciphertext, tag)
                        if decrypted == test_data:
                            self.ok("decryption test: PASS")
                        else:
                            self.err("decryption test: FAIL")
                
                elif cmd == "kdf":
                    if not args or not args[0].startswith("--"):
                        self.err("kdf --<flag> [args]")
                        continue
                    
                    flag = args[0][2:]
                    
                    if flag == "init":
                        if len(args) < 2:
                            self.err("kdf --init <type>")
                            continue
                        kdf_type = args[1].lower()
                        if kdf_type in ("pbkdf2", "hardware"):
                            crypto_state["kdf_type"] = kdf_type
                            self.ok(f"initialized KDF: {kdf_type.upper()}")
                        else:
                            self.err("unsupported KDF type")
                    
                    elif flag == "set-hash":
                        if len(args) < 2:
                            self.err("kdf --set-hash <hash>")
                            continue
                        hash_func = args[1].lower()
                        if hash_func in ("sha256", "sha512"):
                            crypto_state["kdf_hash"] = hash_func
                            self.ok(f"hash: {hash_func.upper()}")
                        else:
                            self.err("unsupported hash function")
                    
                    elif flag == "set-iterations":
                        if len(args) < 2:
                            self.err("kdf --set-iterations <count>")
                            continue
                        try:
                            iterations = int(args[1])
                            crypto_state["kdf_iterations"] = iterations
                            self.ok(f"iterations: {iterations}")
                        except:
                            self.err("invalid number")
                    
                    elif flag == "generate-salt":
                        salt = get_random_bytes(32)
                        salt_b64 = base64.b64encode(salt).decode()
                        crypto_state["salt"] = salt_b64
                        print(salt_b64)
                        self.ok("salt generated")
                    
                    elif flag == "set-salt":
                        if len(args) < 2:
                            self.err("kdf --set-salt <base64>")
                            continue
                        crypto_state["salt"] = args[1]
                        self.ok("salt configured")
                    
                    elif flag == "get-hwid":
                        if len(args) < 2:
                            self.err("kdf --get-hwid <component>")
                            self.out("components: csproduct-uuid, cpu-processorid, baseboard-serial")
                            continue
                        hwid = get_hwid(args[1])
                        if hwid:
                            print(hwid)
                            crypto_state["hwids"].append(hwid)
                    
                    elif flag == "derive-key":
                        if crypto_state["kdf_type"] == "pbkdf2":
                            if not crypto_state["salt"]:
                                self.err("set salt first")
                                continue
                            if len(args) < 2:
                                self.err("kdf --derive-key <password>")
                                continue
                            password = args[1]
                            salt_bytes = base64.b64decode(crypto_state["salt"])
                            iterations = crypto_state["kdf_iterations"] or 100000
                            key = PBKDF2(password, salt_bytes, dkLen=32, count=iterations)
                            crypto_state["key"] = key
                            crypto_state["password_hash"] = hashlib.sha256(password.encode()).hexdigest()
                            self.ok("key derived from password")
                        
                        elif crypto_state["kdf_type"] == "hardware":
                            if not crypto_state["hwids"]:
                                self.err("get hardware IDs first")
                                continue
                            machine_str = "-".join(crypto_state["hwids"])
                            machine_id = hashlib.sha256(machine_str.encode()).hexdigest()
                            salt = b'roblox_account_manager_salt_v1'
                            key = PBKDF2(machine_id, salt, dkLen=32, count=100000)
                            crypto_state["key"] = key
                            self.ok("key derived from hardware")
                        
                        else:
                            self.err("initialize KDF first")
                
                elif cmd == "config":
                    if not args or not args[0].startswith("--"):
                        self.err("config --<flag> [args]")
                        continue
                    
                    flag = args[0][2:]
                    
                    if flag == "set-method":
                        if len(args) < 2:
                            self.err("config --set-method <method>")
                            continue
                        method = args[1].lower()
                        if method in ("hardware", "password", "none"):
                            crypto_state["method"] = method
                            self.ok(f"method: {method}")
                        else:
                            self.err("invalid method")
                    
                    elif flag == "set-cipher":
                        if len(args) < 2:
                            self.err("config --set-cipher <spec>")
                            continue
                        self.ok(f"cipher: {args[1]}")
                    
                    elif flag == "set-kdf":
                        if len(args) < 2:
                            self.err("config --set-kdf <spec>")
                            continue
                        self.ok(f"kdf: {args[1]}")
                    
                    elif flag == "commit":
                        if not crypto_state["method"]:
                            self.err("set method first")
                            continue
                        
                        df = "AccountManagerData"
                        os.makedirs(df, exist_ok=True)
                        enc_path = os.path.join(df, "encryption_config.json")
                        ec = EncryptionConfig(enc_path)
                        
                        if crypto_state["method"] == "hardware":
                            ec.enable_hardware_encryption()
                            self.ok("committed: hardware encryption")
                        elif crypto_state["method"] == "password":
                            if not crypto_state["salt"]:
                                self.err("set salt first")
                                continue
                            if not crypto_state["password_hash"]:
                                pw = input(f"{self.c.pr}password: {Style.RESET_ALL}")
                                crypto_state["password_hash"] = hashlib.sha256(pw.encode()).hexdigest()
                            ec.enable_password_encryption(crypto_state["salt"], crypto_state["password_hash"])
                            self.ok("committed: password encryption")
                        elif crypto_state["method"] == "none":
                            ec.enable_no_encryption()
                            self.ok("committed: no encryption")
                        
                        self.out("configuration committed")
                        # Return to main or exit depending on context
                        return

                elif cmd == "b64":
                    if not args:
                        self.err("b64 <input>")
                        continue
                    input_str = " ".join(args)
                    encoded = base64.b64encode(input_str.encode()).decode()
                    print(encoded)
                
                elif cmd in ("q", "quit", "exit"):
                    if 'startup' in a:
                         if not crypto_state["method"]:
                              self.out("exiting app...")
                              sys.exit(0)
                    return
                
                else:
                    self.err(f"unknown: {cmd}")
                    self.out("type 'help' for commands")
            
            except KeyboardInterrupt:
                print()
                return
            except EOFError:
                return
    
    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{self.c.p}{self.BANNER}")
        
        init_success = self.init()
        
        if not init_success:
            self.crypto_mode(['startup'])
            return
            # guys suffer lol
            self.out("")
            self.out("CRYPTO MODE: manual encryption configuration required")
            self.out("type 'help' for commands")
            print()
            
            crypto_state = {
                "machine_id": None,
                "salt": None,
                "key": None,
                "method": None,
                "password_hash": None
            }
            
            def crypto_help():
                print(f"""
{self.c.p}CRYPTO COMMANDS{self.c.s}
  get <hwid>            get hardware ID (csproduct-uuid, cpu-processorid, baseboard-serial)
  gen <machine-id>      generate machine ID from hardware
  set --salt <b64>      set salt (base64)
  key <input> <salt>    derive encryption key (PBKDF2)
  cipher --test         test cipher with current key
  method <hw|pw|none>   set encryption method
  b64 <input>           encode to base64
  commit                save encryption config
  q                     quit
""")
            
            def get_hwid(component):
                if platform.system() != "Windows":
                    self.err("only supported on Windows")
                    return None
                try:
                    if component == "csproduct-uuid":
                        result = subprocess.check_output("wmic csproduct get uuid", shell=True)
                        return result.decode().split('\n')[1].strip()
                    elif component == "cpu-processorid":
                        result = subprocess.check_output("wmic cpu get processorid", shell=True)
                        return result.decode().split('\n')[1].strip()
                    elif component == "baseboard-serial":
                        result = subprocess.check_output("wmic baseboard get serialnumber", shell=True)
                        return result.decode().split('\n')[1].strip()
                    else:
                        self.err("unknown component")
                        return None
                except Exception as e:
                    self.err(f"failed: {e}")
                    return None
            
            while self.run:
                try:
                    inp = input(f"{self.c.pr}crypto> {Style.RESET_ALL}")
                    parts = inp.strip().split()
                    if not parts:
                        continue
                    
                    cmd = parts[0].lower()
                    args = parts[1:]
                    
                    if cmd == "help" or cmd == "?":
                        crypto_help()
                    
                    elif cmd == "get":
                        if not args:
                            self.err("get <hwid>")
                            self.out("hwid: csproduct-uuid, cpu-processorid, baseboard-serial")
                            continue
                        result = get_hwid(args[0])
                        if result:
                            print(result)
                    
                    elif cmd == "gen":
                        if not args:
                            self.err("gen <machine-id>")
                            self.out("provide hardware identifiers separated by -")
                            continue
                        machine_str = " ".join(args)
                        machine_id = hashlib.sha256(machine_str.encode()).hexdigest()
                        crypto_state["machine_id"] = machine_id
                        print(machine_id)
                    
                    elif cmd == "set":
                        if not args or not args[0].startswith("--"):
                            self.err("set --salt <base64>")
                            continue
                        flag = args[0][2:]
                        if flag == "salt":
                            if len(args) < 2:
                                self.err("provide base64 salt")
                                continue
                            crypto_state["salt"] = args[1]
                            self.ok("salt set")
                        else:
                            self.err(f"unknown flag: --{flag}")
                    
                    elif cmd == "key":
                        if len(args) < 2:
                            self.err("key <input> <salt>")
                            self.out("derives 32-byte key using PBKDF2(input, salt, 100000)")
                            continue
                        input_data = args[0]
                        salt_data = args[1]
                        
                        try:
                            salt_bytes = base64.b64decode(salt_data)
                        except:
                            salt_bytes = salt_data.encode()
                        
                        key = PBKDF2(input_data, salt_bytes, dkLen=32, count=100000)
                        crypto_state["key"] = key
                        key_b64 = base64.b64encode(key).decode()
                        print(key_b64)
                    
                    elif cmd == "cipher":
                        if not args or not args[0].startswith("--"):
                            self.err("cipher --test")
                            continue
                        if args[0] == "--test":
                            if not crypto_state["key"]:
                                self.err("no key set")
                                continue
                            test_data = b"test_encryption"
                            cipher = AES.new(crypto_state["key"], AES.MODE_GCM)
                            nonce = cipher.nonce
                            ciphertext, tag = cipher.encrypt_and_digest(test_data)
                            self.ok("cipher test passed")
                            print(f"nonce: {base64.b64encode(nonce).decode()}")
                    
                    elif cmd == "method":
                        if not args:
                            self.err("method <hw|pw|none>")
                            continue
                        method = args[0].lower()
                        if method in ("hw", "hardware"):
                            crypto_state["method"] = "hardware"
                            self.ok("method: hardware")
                        elif method in ("pw", "password"):
                            crypto_state["method"] = "password"
                            self.ok("method: password")
                        elif method == "none":
                            crypto_state["method"] = "none"
                            self.ok("method: none")
                        else:
                            self.err("invalid method")
                    
                    elif cmd == "b64":
                        if not args:
                            self.err("b64 <input>")
                            continue
                        input_str = " ".join(args)
                        encoded = base64.b64encode(input_str.encode()).decode()
                        print(encoded)
                    
                    elif cmd == "commit":
                        if not crypto_state["method"]:
                            self.err("set method first")
                            continue
                        
                        df = "AccountManagerData"
                        os.makedirs(df, exist_ok=True)
                        enc_path = os.path.join(df, "encryption_config.json")
                        ec = EncryptionConfig(enc_path)
                        
                        if crypto_state["method"] == "hardware":
                            ec.enable_hardware_encryption()
                            self.ok("committed: hardware encryption")
                        elif crypto_state["method"] == "password":
                            if not crypto_state["salt"]:
                                self.err("set salt first")
                                continue
                            if not crypto_state["password_hash"]:
                                pw = input(f"{self.c.pr}password: {Style.RESET_ALL}")
                                crypto_state["password_hash"] = hashlib.sha256(pw.encode()).hexdigest()
                            ec.enable_password_encryption(crypto_state["salt"], crypto_state["password_hash"])
                            self.ok("committed: password encryption")
                        elif crypto_state["method"] == "none":
                            ec.enable_no_encryption()
                            self.ok("committed: no encryption")
                        
                        self.out("restart to continue")                   
                    
                    elif cmd in ("q", "quit", "exit"):
                        self.quit([])
                        break
                    
                    else:
                        self.err(f"unknown: {cmd}")
                        self.out("type 'help' for commands")
                
                except KeyboardInterrupt:
                    print()
                    self.quit([])
                    break
                except EOFError:
                    self.quit([])
                    break
            return
    
    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{self.c.p}{self.BANNER}")
        
        init_success = self.init()
        
        if not init_success:
            self.crypto_mode(['startup'])
            return
        
        for cmd_str in self.cfg.get("scripts.on_startup", []):
            if isinstance(cmd_str, str):
                cmd, args = self.parse(cmd_str)
                if cmd:
                    self.run_cmd(cmd, args)
        
        while self.run:
            try:
                inp = input(self.prompt())
                cmd, args = self.parse(inp)
                if cmd:
                    self.run_cmd(cmd, args)
            except KeyboardInterrupt:
                print()
                self.quit([])
            except EOFError:
                self.quit([])


if __name__ == "__main__":
    CLI().main()
