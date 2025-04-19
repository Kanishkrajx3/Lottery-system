import time
import random
import threading
import signal
import string
import os
from datetime import datetime, timedelta


users = set()
lock = threading.Lock()
log_file = 'lottery_log.txt'
backup_file = 'backup_users.txt'
start_time = datetime.now()
registration_period = timedelta(minutes=2)
extended_period = timedelta(minutes=30)
next_backup_time = time.time() + 300 
registration_end_time = start_time + registration_period
extended = False
running = True


def log(msg):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")


def save_backup():
    with open(backup_file, 'w') as f:
        for user in users:
            f.write(f"{user}\n")


def load_backup():
    if os.path.exists(backup_file):
        with open(backup_file, 'r') as f:
            for line in f:
                users.add(line.strip())


def time_announcer():
    while running:
        time.sleep(600)  
        with lock:
            if running:
                time_left = max((registration_end_time - datetime.now()).total_seconds(), 0)
                mins = int(time_left // 60)
                print(f"\n[INFO] Time remaining for registration: {mins} minute(s)")
                print(f"[INFO] Registered users: {len(users)}\n")


def signal_handler(sig, frame):
    print("\n[INFO] Program interrupted. Saving progress...")
    with lock:
        save_backup()
        log("Program interrupted. Backup saved.")
        print("[INFO] Backup saved. Exiting.")
    exit(0)


def is_valid_username(username):
    if not username:
        return False
    allowed = string.ascii_letters + string.digits + "_"
    return all(char in allowed for char in username)


def register_users():
    global registration_end_time, extended, running
    while datetime.now() < registration_end_time:
        username = input("Enter a unique username to register: ").strip()

        if not is_valid_username(username):
            print("[ERROR] Invalid username. Use letters, digits, and underscores only.")
            continue

        with lock:
            if username in users:
                print("[ERROR] Username already registered.")
                continue

            users.add(username)
            log(f"User registered: {username}")
            print(f"[INFO] {username} registered successfully. Total users: {len(users)}")

        if time.time() > next_backup_time:
            with lock:
                save_backup()


    if len(users) < 5 and not extended:
        print("\n[INFO] Less than 5 users registered. Extending registration by 30 minutes...")
        registration_end_time = datetime.now() + extended_period
        extended = True
        register_users()  # Call again for extension
    elif len(users) == 0:
        print("[INFO] No users registered. Exiting.")
        log("No users registered. Lottery ended with no participants.")
        running = False
        return


def pick_winner():
    print("\n[INFO] Registration period ended.")
    if len(users) == 0:
        print("[INFO] No participants. Exiting.")
        return

    winner = random.choice(list(users))
    print("\n🎉🎉🎉 Lottery Winner 🎉🎉🎉")
    print(f"Winner: {winner}")
    print(f"Total Participants: {len(users)}")
    print("Thank you for participating!")

    log(f"Winner declared: {winner}")
    log(f"Total Participants: {len(users)}")


    if os.path.exists(backup_file):
        os.remove(backup_file)


def main():
    print("=== Welcome to the Terminal Lottery System ===")
    print("Registration is open for 2 min.")
    print("You will be prompted to enter your username.")

    signal.signal(signal.SIGINT, signal_handler)
    load_backup()

    
    announcer = threading.Thread(target=time_announcer, daemon=True)
    announcer.start()

    
    register_users()

    if running:
        pick_winner()

if __name__ == "__main__":
    main()
