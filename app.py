import tkinter as tk
import requests
import json
import threading
import time
import os
from tkinter import PhotoImage

API_URL = "https://esplay.com/api/profile/get?username={}&game_stats=1&game_id=1&steam=1"

# Ensure the "json" directory exists
if not os.path.exists("json"):
    os.makedirs("json")

def calculate_stats(data):
    if data['cs_fields']['deaths'] > 0:
        kd = round(data['cs_fields']['kills'] / data['cs_fields']['deaths'], 2)
    else:
        kd = data['cs_fields']['kills']
    
    if data['game_stats']['matches'] > 0:
        win_percentage = round((data['game_stats']['wins'] / data['game_stats']['matches']) * 100, 0)
    else:
        win_percentage = "N/A"
    
    if data['cs_fields']['kills'] > 0:
        hs_percentage = round((data['cs_fields']['headshots'] / data['cs_fields']['kills']) * 100, 0)
    else:
        hs_percentage = "N/A"
    
    if data['cs_fields']['rounds'] > 0:
        adr = round(data['cs_fields']['damage_dealt'] / data['cs_fields']['rounds'], 2)
    else:
        adr = "N/A"

    elo = data['game_stats']['elo']

    if elo is None:
        elo_image = "default.png"
    elif elo >= 2300:
        elo_image = "global.png"
    elif elo >= 2100:
        elo_image = "elite_3.png"
    elif elo >= 2000:
        elo_image = "elite_2.png"
    elif elo >= 1900:
        elo_image = "elite_1.png"
    elif elo >= 1700:
        elo_image = "diamond_3.png"
    elif elo >= 1600:
        elo_image = "diamond_2.png"
    elif elo >= 1500:
        elo_image = "diamond_1.png"
    elif elo >= 1300:
        elo_image = "gold_3.png"
    elif elo >= 1200:
        elo_image = "gold_2.png"
    elif elo >= 1100:
        elo_image = "gold_1.png"
    elif elo >= 1000:
        elo_image = "silver_2.png"
    else:
        elo_image = "silver_1.png"
    
    return {
        "username": data["username"],
        "elo": elo,
        "kd": kd,
        "win_percentage": win_percentage,
        "hs_percentage": hs_percentage,
        "adr": adr,
        "elo_image": elo_image,
    }

def fetch_data(username, initial=False):
    url = API_URL.format(username)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Save the data in the "json" folder
        filename = f"json/updated_{username}.json"
        if initial:
            filename = f"json/start_app_{username}.json"

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Data saved to {filename}")
        if not initial:
            print(f"Updated data for {username} in {filename}")
        
        return data

    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None

def auto_refresh(username):
    while True:
        data = fetch_data(username)
        if data:
            update_display(data)
        time.sleep(60)

def submit():
    username = entry.get().strip()
    if username:
        data = fetch_data(username, initial=True)
        if data:
            update_display(data)

        enter_username_label.pack_forget()
        entry.pack_forget()
        submit_button.pack_forget()

        thread = threading.Thread(target=auto_refresh, args=(username,), daemon=True)
        thread.start()

def update_display(data):
    stats = calculate_stats(data)

    # Set the text for the labels
    username_label.config(text=f"{stats['username']} ({stats['elo']})")
    kd_label.config(text=f"K/D: {stats['kd']}")
    adr_label.config(text=f"ADR: {stats['adr']}")
    win_percentage_label.config(text=f"Win%: {stats['win_percentage']}")
    hs_percentage_label.config(text=f"HS%: {stats['hs_percentage']}")

    # Set the Elo image
    elo_image = PhotoImage(file=f"images/elo/{stats['elo_image']}")
    elo_image_label.config(image=elo_image)
    elo_image_label.image = elo_image

    # Clear the grid before updating
    for widget in widget_frame.grid_slaves():
        widget.grid_forget()

    # Elo image stays in the first column, spanning all three rows
    elo_image_label.grid(row=0, column=0, rowspan=3, sticky="nsew")

    # Name and Elo span columns 1-2 on row 0
    username_label.grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=1)
    elo_label.grid(row=0, column=1, sticky="w", padx=0, pady=0)

    # K/D and ADR on row 1
    kd_label.grid(row=1, column=1, sticky="w", padx=5, pady=1)
    adr_label.grid(row=1, column=2, sticky="w", padx=5, pady=1)

    # Win% and HS% on row 2
    win_percentage_label.grid(row=2, column=1, sticky="w", padx=5, pady=1)
    hs_percentage_label.grid(row=2, column=2, sticky="w", padx=5, pady=1)

root = tk.Tk()
root.title("Username Fetcher")

enter_username_label = tk.Label(root, text="Enter Username:")
enter_username_label.pack(pady=5)

entry = tk.Entry(root)
entry.pack(pady=5)

submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack(pady=10)

widget_frame = tk.Frame(root)
widget_frame.pack(pady=20)

widget_frame.grid_rowconfigure(0, weight=1)  # Row for Name and Elo
widget_frame.grid_rowconfigure(1, weight=1)  # Row for K/D and ADR
widget_frame.grid_rowconfigure(2, weight=1)  # Row for Win% and HS%
widget_frame.grid_columnconfigure(0, weight=1)  # Image column (on the left)
widget_frame.grid_columnconfigure(1, weight=2)  # Name and Stats columns (left part)
widget_frame.grid_columnconfigure(2, weight=2)  # Stats columns (right part)

elo_image_label = tk.Label(widget_frame)
elo_image_label.grid(row=0, column=0, rowspan=3, sticky="nsew")

username_label = tk.Label(widget_frame, font=("Arial", 20, "bold"))
elo_label = tk.Label(widget_frame, font=("Arial", 20, "bold"))
kd_label = tk.Label(widget_frame, font=("Arial", 18, "bold"))
adr_label = tk.Label(widget_frame, font=("Arial", 18, "bold"))
win_percentage_label = tk.Label(widget_frame, font=("Arial", 18, "bold"))
hs_percentage_label = tk.Label(widget_frame, font=("Arial", 18, "bold"))

root.mainloop()
