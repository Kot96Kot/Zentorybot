from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from zentory.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield
