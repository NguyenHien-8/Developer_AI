# ============================================ Nguyen Hien ============================================ 
# Developer: Trần Nguyên Hiền
# Faculty: Electronics and Communication Engineering
# =====================================================================================================
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import threading
import uvicorn
from typing import List
import asyncio

import sounddevice as sd
import queue
import json
import re
import os
import tempfile
from vosk import Model, KaldiRecognizer
from rapidfuzz import fuzz
from gtts import gTTS
import pygame
import time
from Installsubabase import supabase

app = FastAPI(title="Voice Ordering System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
active_websockets: List[WebSocket] = []
is_speaking = False
latest_order = None
drink_prices = {}
audio_stream = None
is_started = False

# ============= From Supabase Import Drink and Ingredient =============
def fetch_drinks_from_supabase():
    try:
        response = supabase.table("drinkdata").select("drink_name,price").execute()
        drink_list = []
        for item in response.data:
            name = item.get('drink_name', '').lower()
            price = item.get('price', 0)
            if name:
                drink_list.append({"name": name, "price": price})
        return drink_list
    except Exception as e:
        print("Error fetching drinks from Supabase:", str(e))
        return []

def fetch_components_from_supabase():
    try:
        response = supabase.table("drinkdata").select("drink_name,ingredients").execute()
        comp_dict = {}
        for item in response.data:
            name = item.get("drink_name", "").lower()
            ing = item.get("ingredients", "")
            if name and isinstance(ing, str):
                ing = ing.strip("{}") 
                comp_dict[name] = [i.strip().lower() for i in ing.split(",") if i.strip()]
        return comp_dict
    except Exception as e:
        print("Error fetching ingredients from Supabase:", str(e))
        return {}

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def update_drink_keywords(drink_data):
    keywords["Drink"] = {}
    for item in drink_data:
        name = item["name"]
        price = item["price"]
        clean_name = normalize_text(name)
        keywords["Drink"][clean_name] = [clean_name]
        drink_prices[clean_name] = price

# ========================== Text-To-Speech ===========================
def speak(text):
    global is_speaking, audio_stream
    if not text.strip():
        return
    is_speaking = True
    print(f"[assistantSpeak]: {text}")
    # Send [assistantSpeak]: {text} to Websocket
    asyncio.run(broadcast_to_clients({"type": "assistantSpeak", "text": text}))
    tts = gTTS(text=text, lang='en')
    temp_dir = os.path.join(os.getcwd(), "Voice")
    os.makedirs(temp_dir, exist_ok=True)
    mp3_path = os.path.join(temp_dir, "tts.mp3")
    tts.save(mp3_path)

    if audio_stream is not None:
        audio_stream.stop()
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    os.unlink(mp3_path)

    if audio_stream is not None:
        audio_stream.start()
    is_speaking = False
    
# ========================= Voice Recognition =========================
q = queue.Queue()
model_en = Model("vosk-model-small-en-us-0.15")
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])
rec = KaldiRecognizer(model_en, samplerate)
rec.SetWords(True)

def callback(indata, frames, time_, status):
    global is_speaking
    if status:
        print("Audio Error:", status)
    if not is_speaking:
        q.put(bytes(indata))

# ============================= Keywords =============================
keywords = {
    "Drink": {},
    "Size": {
        "S": ["size s", "size small", "small"],
        "M": ["size m", "size medium", "medium"],
        "L": ["size l", "size large", "large"]
    },
    "YesNo": {
        "Yes": ["yes", "yeah", "correct", "sure", "right", "ok"],
        "No": ["no", "nope", "not", "incorrect", "wrong"]
    }
}
TRIGGER_KEYWORDS = ["hey abm","hey a bm", "hey ab m", "hey a b m", "hey",
                    "hey apm", "hey a p m", "hey ap m", "hey a pm",
                    "abm", "a b m", "ab m", "a b m",
                    "apm", "a p m", "ap m", "a pm",
                   "hey ibm","hey i bm", "hey ib m", "hey i b m",
                    "hey ipm", "hey i p m", "hey ip m", "hey i pm",
                    "ibm", "i b m", "ib m", "i b m",
                    "ipm", "i p m", "ip m", "i pm",
                   "hey abem","hey a bem", "hey ab em", "hey a b em",
                    "hey apem", "hey a p em", "hey ap em", "hey a pem",
                    "abem", "a b em", "ab em", "a b em",
                    "apem", "a p em", "ap em", "a pem",
                   "hey ibam","hey i bam", "hey ib am", "hey i b am",
                    "hey ipam", "hey i p am", "hey ip am", "hey i pam",
                    "ibam", "i b am", "ib am", "i b am",
                    "ipam", "i p am", "ip am", "i pam",
                   "hey abam","hey a bam", "hey ab am", "hey a b am",
                    "hey apam", "hey a p am", "hey ap am", "hey a pam",
                    "abam", "a b am", "ab am", "a b am",
                    "apam", "a p am", "ap am", "a pam",
                   "hey ibem","hey i bem", "hey ib em", "hey i b em",
                    "hey ipem", "hey i p em", "hey ip em", "hey i pem",
                    "ibem", "i b em", "ib em", "i b em",
                    "ipem", "i p em", "ip em", "i pem",]

def detect_best_match(text, category, threshold=80):
    for label, kw_list in keywords[category].items():
        for kw in kw_list:
            if text.strip() == kw.strip():
                return label
    best_match = {"score": 0, "label": None, "length": 0}
    for label, kw_list in keywords[category].items():
        for kw in kw_list:
            score = fuzz.partial_ratio(text, kw)
            if score > best_match["score"] or (
                score == best_match["score"] and len(kw.split()) > best_match["length"]
            ):
                best_match.update({"score": score, "label": label, "length": len(kw.split())})
    if best_match["score"] >= threshold:
        return best_match["label"]
    return None

def is_valid_speech(text):
    if not text:
        return False
    if any(kw in text for kw in TRIGGER_KEYWORDS):
        return True
    for category in keywords.values():
        for kw_list in category.values():
            for kw in kw_list:
                if kw in text:
                    return True
    return False

def reset_state():
    global selected_drink, selected_size, component_sizes
    global customizing, current_component_index
    global step, waiting_confirmation, pending_value, pending_category

    selected_drink = None
    selected_size = None
    component_sizes.clear()
    customizing = False
    current_component_index = 0
    step = 1
    waiting_confirmation = False
    pending_value = None
    pending_category = None

# ============ Initialize Keywords And Data ============
drink_data = fetch_drinks_from_supabase()
update_drink_keywords(drink_data)
components = fetch_components_from_supabase()

print("Updated drink keywords:", keywords["Drink"])
print("Updated components from Supabase:", components)

# ============= MAIN VOICE ORDER FUNCTION ==============
def Voice_Ordering_System():
    global step, selected_drink, selected_size
    global waiting_confirmation, pending_value, pending_category
    global customizing, current_component_index, component_sizes
    global listening_for_trigger, latest_order
    global audio_stream, is_started
    
    trigger_keywords = TRIGGER_KEYWORDS
    print(f"Listening... (Sample Rate = {samplerate})")

    step = 1
    selected_drink = None
    selected_size = None
    waiting_confirmation = False
    pending_value = None
    pending_category = None
    customizing = False
    current_component_index = 0
    component_sizes = {}
    listening_for_trigger = True
    latest_order = None

    audio_stream = sd.RawInputStream(samplerate=samplerate, blocksize=4000, dtype='int16', channels=1, callback=callback)
    with audio_stream:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = normalize_text(result.get("text", ""))
                print(f"[userSpeak]: {text}")
                # Send [userSpeak]: {text} to Websocket
                if is_started and text:
                    asyncio.run(broadcast_to_clients({"type": "userSpeak", "text": text}))
                
                if is_speaking or not text or not is_valid_speech(text):
                    print("Ignored noise or system playback.")
                    continue

                if listening_for_trigger:
                    if text.startswith("autobarista") or any(kw in text for kw in trigger_keywords):
                        asyncio.run(broadcast_to_clients({"type": "start"}))
                        is_started = True
                        speak("Yes,I'm here. What would you like to drink?")
                        print("Yes,I'm here. What would you like to drink?")
                        listening_for_trigger = False
                        step = 1
                    else:
                        print("Waiting for trigger word...")
                    continue

                if waiting_confirmation:
                    answer = detect_best_match(text, "YesNo")
                    if answer == "Yes":
                        if pending_category == "Drink":
                            selected_drink = pending_value
                            if selected_drink in components:
                                speak(f"You choose {selected_drink}. Would you like to customize the ingredients?")
                                pending_category = "CustomizeChoice"
                                waiting_confirmation = True
                            else:
                                speak(f"You choose {selected_drink}. What size would you like?")
                                step = 2
                                waiting_confirmation = False
                        elif pending_category == "CustomizeChoice":
                            customizing = True
                            current_component_index = 0
                            component_sizes.clear()
                            comp = components[selected_drink][current_component_index]
                            speak(f"What size for {comp}?")
                            step = 3
                            waiting_confirmation = False
                        elif pending_category == "Size":
                            selected_size = pending_value
                            price = drink_prices.get(selected_drink, "unknown")
                            component_list = components.get(selected_drink, [])
                            component_sizes = {comp: selected_size for comp in component_list}
                            latest_order = {
                               "drink": selected_drink,
                               "details": {
                                   "price": price,
                                   **component_sizes.copy(),
                                }
                            }
                            speak(f"Confirm: {selected_drink} - size {selected_size}. The price is {price*1000} vnd. Does this seem right to you?")
                            pending_category = "FinalConfirmation"
                        elif pending_category == "FinalConfirmation":
                            price = drink_prices.get(selected_drink, "unknown")
                            speak(f"Order successful! Enjoy your {selected_drink}.")
                            asyncio.run(broadcast_to_clients({
                                "type": "voiceOrderResult",
                                "data": latest_order
                            }))
                            reset_state()
                            listening_for_trigger = True
                            is_started = False
                            speak("If you want to order again, just say hey ABM")
                    elif answer == "No":
                        if pending_category == "Drink":
                            speak("Sorry, I did not catch that. What would you like to drink?")
                            step = 1
                            waiting_confirmation = False
                        elif pending_category == "CustomizeChoice":
                            speak(f"Please say again, what size for your {selected_drink}?")
                            step = 2
                            waiting_confirmation = False
                        elif pending_category == "FinalConfirmation":
                            if customizing:
                                current_component_index = 0
                                component_sizes.clear()
                                comp = components[selected_drink][current_component_index]
                                speak(f"Don't worry — let try again. What size {comp} would you like?")
                                step = 3
                            else:
                                speak("Sorry, could you say the size again?")
                                step = 2
                            waiting_confirmation = False
                    else:
                        speak("You can answer yes or no.")
                    continue

                if step == 1:
                    drink = detect_best_match(text, "Drink")
                    if drink:
                        speak(f"You said {drink}, did you mean a drink {drink}?")
                        pending_value = drink
                        pending_category = "Drink"
                        waiting_confirmation = True
                    else:
                        speak("Sorry, I did not quite get the drink. Mind saying it one more time?")

                elif step == 2:
                    size = detect_best_match(text, "Size")
                    if size:
                        selected_size = size
                        price = drink_prices.get(selected_drink, "unknown")
                        component_list = components.get(selected_drink, [])
                        component_sizes = {comp: selected_size for comp in component_list}
                        latest_order = {
                           "drink": selected_drink,
                           "details": {
                               "price": price,
                                **component_sizes.copy(),
                            }
                        }
                        speak(f"Confirm: {selected_drink} - size {selected_size}. The price is {price*1000} vnd. Does this seem right to you?")
                        pending_category = "FinalConfirmation"
                        waiting_confirmation = True
                    else:
                        speak("Sorry, I did not quite get the size. Mind saying it one more time?")

                elif step == 3:
                    size = detect_best_match(text, "Size")
                    if size:
                        comp = components[selected_drink][current_component_index]
                        component_sizes[comp] = size
                        current_component_index += 1
                        
                        if current_component_index < len(components[selected_drink]):
                            next_comp = components[selected_drink][current_component_index]
                            speak(f"What size for {next_comp}?")
                        else:
                            price = drink_prices.get(selected_drink, "unknown")
                            final_text = f"Confirm: {selected_drink} with " + \
                                         ", ".join([f"{k} size {v}" for k, v in component_sizes.items()])
                            latest_order = {
                                "drink": selected_drink,
                                "details": {
                                    "price": price,
                                    **component_sizes.copy(),
                                }
                            }
                            speak(f"{final_text}. The price is {price*1000} vnd. Is this correct?")
                            pending_category = "FinalConfirmation"
                            waiting_confirmation = True
                    else:
                        speak("Sorry, I did not quite get the size. Mind saying it one more time?")

# ======================== WEBSOCKET ========================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()  
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        print("Client disconnected")

async def broadcast_to_clients(message: dict):
    for ws in active_websockets:
        try:
            await ws.send_json(message)
        except Exception as e:
            print("WebSocket Send Error:", e)

@app.on_event("startup")
def start_background_thread():
    thread = threading.Thread(target=Voice_Ordering_System, daemon=True)
    thread.start()
    print("Voice System Started In Background.")
    
if __name__ == "__main__":
    uvicorn.run("WebSocket_Speech_VoskAPI:app", host="0.0.0.0", port=8086, reload=False)
    
