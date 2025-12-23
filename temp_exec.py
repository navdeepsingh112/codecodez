import time
import random

def analyze_data():
    print("Initializing analysis engine...")
    time.sleep(1)
    
    items = ["Server-A", "Server-B", "Database-Main"]
    
    for item in items:
        status = "ONLINE" if random.random() > 0.2 else "OFFLINE"
        print(f"Checking {item}... [{status}]")
        time.sleep(0.5)
        
    print("-" * 20)
    print("Process Complete.")

if __name__ == "__main__":
    analyze_data()

