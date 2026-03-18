import uvicorn
import logging
import sys

# Forzar logging a stdout
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("startup")

if __name__ == "__main__":
    logger.info("Iniciando servidor API desde script manual...")
    try:
        logger.info("Importando app.main...")
        import app.main
        app = app.main.app
        logger.info("App importada exitosamente.")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    except Exception as e:
        logger.error(f"FALLO CRÍTICO EN STARTUP: {e}", exc_info=True)
        sys.exit(1)
