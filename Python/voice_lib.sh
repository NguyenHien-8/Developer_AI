cd ..
source venv/bin/activate
pip install fastapi uvicorn sounddevice vosk rapidfuzz gTTS pydub supabase pygame
sudo apt install libportaudio2 libportaudiocpp0 portaudio19-dev
pip uninstall sounddevice
pip install sounddevice
