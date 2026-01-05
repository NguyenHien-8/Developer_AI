echo "Starting voice service..."
cd ..
source venv/bin/activate
cd Voice
python3 WebSocket_Speech_VoskAPI.py
echo "Voice service ended"
