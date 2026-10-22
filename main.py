from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import auth, task, team, user
from exceptions import BaseError

app = FastAPI(
    title="NEXORA API",
    summary="Tasks, teams and team chat for the NEXORA web app.",
)

# The web app is a separate static site, so the API accepts cross-origin calls.
# Auth uses Bearer tokens rather than cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth.router, user.router, task.router, team.router):
    app.include_router(router)


@app.exception_handler(BaseError)
async def handle_domain_error(_: Request, error: BaseError) -> JSONResponse:
    """Turn domain errors into `{"detail": message}` with the error's status code."""
    return JSONResponse({"detail": error.message}, status_code=error.status_code)
