import logging.config
from src.config import LOGGING

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    logging.config.dictConfig(LOGGING)
    uvicorn.run(app, host="0.0.0.0", port=8080)
