from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
import logging

from database import Base, engine
from dependances import limiter

from routes.comptes import router as router_comptes
from routes.connexions import router as router_connexion
from routes.transactions import router as router_transactions
from routes.admin import router as router_admin

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

app.include_router(router_comptes)
app.include_router(router_connexion)
app.include_router(router_transactions)
app.include_router(router_admin)