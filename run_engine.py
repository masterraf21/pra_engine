import uvicorn
from src.config import get_settings
# from src.utils.logging import get_logger

if __name__ == "__main__":
    env = get_settings()
    # logger = get_logger(__name__)

    reload = env.environment == "dev"
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=reload, log_config="./log_config.yaml")
