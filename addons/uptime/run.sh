#!/usr/bin/env bash
set -e

echo "============================================================"
echo " Starting Delta Chat Uptime Bot..."
echo "============================================================"

cd /app
export PYTHONUNBUFFERED=1
export DC_DB_DIR="/data"
export DB_PATH="/data/uptime.db"
export PORT="8080"

mkdir -p /root/.config
ln -sfn /data /root/.config/uptimebot

python3 -u - << 'EOF'
import json, os, subprocess, sys, time

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

options = {}
if os.path.exists("/data/options.json"):
    try:
        with open("/data/options.json", "r") as f:
            options = json.load(f)
    except Exception as e:
        print(f"Error reading /data/options.json: {e}")

accounts_dir = "/data/accounts"
has_account = False
if os.path.exists(accounts_dir):
    import glob, sqlite3
    toml_path = os.path.join(accounts_dir, "accounts.toml")
    if os.path.exists(toml_path):
        dbs = glob.glob(os.path.join(accounts_dir, "*", "dc.db"))
        for db in dbs:
            try:
                conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
                cur = conn.cursor()
                cur.execute("SELECT value FROM config WHERE keyname='configured'")
                row = cur.fetchone()
                conn.close()
                if row and str(row[0]) == "1":
                    has_account = True
                    break
            except Exception:
                has_account = True
                break

    if not has_account:
        try:
            from deltachat2 import IOTransport, Rpc
            with IOTransport(accounts_dir=accounts_dir) as trans:
                rpc = Rpc(trans)
                accids = rpc.get_all_account_ids()
                for accid in accids:
                    if rpc.is_configured(accid):
                        has_account = True
                        break
        except Exception:
            pass

if not has_account:
    chatmail_qr = options.get("chatmail_qr", "").strip()
    email = options.get("email", "").strip()
    password = options.get("password", "").strip()
    
    if chatmail_qr:
        print("Initializing Delta Chat account from Chatmail QR / URI...")
        res = subprocess.run(["python3", "bot.py", "-c", "/data", "init", chatmail_qr])
        if res.returncode == 0:
            has_account = True
    elif email and password:
        print(f"Initializing Delta Chat account for {email}...")
        res = subprocess.run(["python3", "bot.py", "-c", "/data", "init", email, password])
        if res.returncode == 0:
            has_account = True
    
    if not has_account:
        print("\n" + "="*60, flush=True)
        print("⚠️  DELTA CHAT ACCOUNT SETUP REQUIRED", flush=True)
        print("="*60, flush=True)
        print("Please configure your bot in Home Assistant:", flush=True)
        print("  1. Go to the 'Configuration' tab for this add-on.", flush=True)
        print("  2. Enter either:", flush=True)
        print("     - 'chatmail_qr': Your Chatmail QR string (DCACCOUNT:...)", flush=True)
        print("     - 'email' & 'password': Your standard mail credentials", flush=True)
        print("  3. Click Save and Restart the add-on.", flush=True)
        print("="*60 + "\n", flush=True)
        while True:
            time.sleep(30)
            print("⏳ Waiting for credentials... Configure in add-on settings and restart.", flush=True)

admin_email = options.get("admin_email", "").strip()
admin_fp = options.get("admin_fingerprint", "").strip()
if admin_email or admin_fp:
    cmd = ["python3", "set_admin.py"]
    if admin_email:
        cmd.extend(["--email", admin_email])
    if admin_fp:
        cmd.extend(["--fingerprint", admin_fp])
    try:
        subprocess.run(cmd)
    except Exception as e:
        print(f"Admin configuration note: {e}")

disp_name = options.get("display_name", "").strip()
status_text = options.get("status_text", "").strip()

try:
    with open("/tmp/bot_env", "w") as ef:
        if disp_name:
            ef.write(f"export DISPLAY_NAME={json.dumps(disp_name)}\n")
        if status_text:
            ef.write(f"export STATUS_TEXT={json.dumps(status_text)}\n")
except Exception:
    pass

try:
    from deltachat2 import IOTransport, Rpc
    with IOTransport(accounts_dir=accounts_dir) as trans:
        rpc = Rpc(trans)
        accids = rpc.get_all_account_ids()
        if accids and rpc.is_configured(accids[0]):
            accid = accids[0]
            if disp_name:
                try:
                    rpc.set_config(accid, "displayname", disp_name)
                except Exception:
                    pass
            if status_text:
                try:
                    rpc.set_config(accid, "selfstatus", status_text)
                except Exception:
                    pass
            link = rpc.get_chat_securejoin_qr_code(accid, None)
            print("\n" + "="*60)
            print("🚀 Delta Chat Bot is ready!")
            print(f"Invite link: {link}")
            try:
                import qrcode
                qr = qrcode.QRCode()
                qr.add_data(link)
                print("\nScan this QR code in your Delta Chat mobile app:")
                qr.print_ascii(invert=True)
            except Exception:
                pass
            print("="*60 + "\n")
except Exception:
    pass
EOF

if [ -f /tmp/bot_env ]; then
    source /tmp/bot_env
    rm -f /tmp/bot_env
fi

echo "Starting bot service..."
exec python3 -u bot.py -c /data serve
