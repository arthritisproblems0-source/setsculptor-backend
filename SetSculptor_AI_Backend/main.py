from fastapi import FastAPI, UploadFile
import librosa, uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SetSculptor Backend Running"}

@app.post("/analyze")
async def analyze(file: UploadFile):
    # Placeholder for audio processing
    return {"status": "File received", "filename": file.filename}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
