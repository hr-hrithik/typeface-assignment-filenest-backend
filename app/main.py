import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud.logging import Client

from app.routers.user_files import router as user_files_router
from app.routers.user import router as user_router
logger = logging.getLogger(__name__)

origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000",
    "*"
]

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins = origins, allow_methods = ['*'], allow_headers = ['*'])

@app.on_event('startup')
def on_startup():
    client = Client()
    logging.basicConfig(
            format="%(asctime)s,%(msecs)d %(name)s %(lineno)d %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            level=logging.INFO,
        )
    client.setup_logging(log_level=logging.INFO)
    logger.info(f"Logger initialised successfully")
    
app.include_router(router=user_router, prefix='/api/v1/users')
app.include_router(router=user_files_router, prefix='/api/v1/files')