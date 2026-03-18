import logging
from app.core.config import settings

# Los módulos pesados (whisper, numpy) se importan de forma perezosa dentro de las funciones
logger = logging.getLogger(__name__)

# Cargar modelo una vez (singleton)
_model = None

def get_whisper_model():
    import whisper
    global _model
    if _model is None:
        logger.info(f"Cargando modelo Whisper '{settings.WHISPER_MODEL}' en CPU...")
        _model = whisper.load_model(settings.WHISPER_MODEL, device="cpu")
        logger.info("Whisper cargado.")
    return _model

async def transcribir_audio(audio_bytes: bytes) -> str:
    import numpy as np
    import io
    import soundfile as sf
    """
    Transcribe audio (formato soportado por Whisper: mp3, wav, etc.) a texto.
    """
    # Whisper espera un numpy array y sample rate.
    # Convertimos bytes a audio con soundfile
    try:
        with io.BytesIO(audio_bytes) as f:
            audio, sr = sf.read(f)
        # Si es estéreo, convertimos a mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        # Whisper requiere sample rate 16000
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        model = get_whisper_model()
        result = model.transcribe(audio, language="es", task="transcribe")
        return result["text"].strip()
    except Exception as e:
        logger.error(f"Error transcribiendo audio: {e}")
        return ""