from typing import Annotated    # Attach extra info on type

from contextlib import asynccontextmanager

from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from database import engine, get_db

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from routers import posts, users

from config import settings

# Connects SQLAlchemy Models to database and creates all tables
# Base.metadata.create_all(bind=engine)

# HTML View

# Async way of creating database tables.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # # Startup
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    
    #Shutdown
    await engine.dispose()


# Creating API
app = FastAPI(lifespan=lifespan)

# Adding folder to take care of path handling
app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect folder to FastAPI, allows HTML to read src files.
# app.mount("/media", StaticFiles(directory="media"), name="media")

# HTML template with data placeholders
templates = Jinja2Templates(directory="templates")

# Adding routes to user.py and post.py
# tags organises documents api
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])


# Health Check Endpoint
@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}


# Home and post directory
@app.get("/", include_in_schema=False, name="home")     # include_in_schema = in api docs?
@app.get("/posts", include_in_schema=False, name="posts")   # name="" used for  url_for("") to return URL
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):     # Don't forget request when returning in HTML
                                #  Stores session connected to database
    
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0
    
    # From database, select Post table
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    
    # Returns All posts as a list
    posts = result.scalars().all()
    
    has_more = len(posts) < total
    
    # Displays home / post page in jinga html
    return templates.TemplateResponse(      # Responds in HTML
        request,                            # The request made by user
        "home.html",                        # The file name to display
        {
            "posts": posts,
            "title": "Home",                    # Replaces placeholders with data
            "limit": settings.posts_per_page,   # Limit posts per page
            "has_more": has_more,               # Has More Pages
        }, 
    )


# View Individual Post with post_id
@app.get("/posts/{post_id}", include_in_schema=False)   # e.g. /posts/1
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):  # post_page function
    
    # From database, select table Post, in column id, find matching id.
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    
    # Return first matching Post object, or None
    post = result.scalars().first()
    
    # for post in posts:  # Iterates through the dictionairy of posts
    #     if post.get("id") == post_id:   # If post id found
    #         title = post['title'][:50]  # Replaces placeholder title to post title
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(      # Responds in HTML
                request,                        # The request made by user
                "post.html",                    # File name to display, i.e. post.html
                {"post": post, "title": title}, # Replaces placeholders in post.html with data
            )
    
    # If not found post, raise 404 error
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# Post Page
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    count_result = await db.execute(
        select(func.count())
        .select_from(models.Post)
        .where(models.Post.user_id == user_id),
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
        
    message = (
        exception.detail
        if exception.detail
        else "An error occured. Please check your request and try again."
    )
        
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message
        },
        status_code=exception.status_code
    )


# Login User
@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )
    
    
# Register User
@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )
    
    
# Account User
@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )
    
    
# Forgot Password
@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"}
    )
    
    
# Reset Password
@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )



