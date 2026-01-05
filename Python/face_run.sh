echo "Starting face service ..."
cd ..
source venv/bin/activate
cd Face
uvicorn main:app --port=8085
echo "Face service start successfully "
