from __future__ import annotations  # Defines classes in the future before reaching them

from datetime import UTC, datetime  # Time

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
# DateTime - Database column type for dates and times.
# ForeignKey - Connects a column to a key in another table
# Integer | String | Text - Database column types

from sqlalchemy.orm import Mapped, mapped_column, relationship
# Mapped - Tells SQLAlchemy what type of value a model attribute represents
# mapped_column - Defines a database column, configuration
# relationship - Defines how two models relate to each other

from database import Base   # Foundation of defining database table

from config import settings

# Creates users table in database

# user.username
# user.email
# user.posts
# user.image_path

class User(Base):
    __tablename__ = "users"  # Name of table
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    #   Type: Integer | Configure | Integer , unique identifier, creates index for query
    
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    #   Type: String  |   Configure | String to 50, prevent duplicate, value required
    
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    #   Type: String  | Configure | String to 120, prevent duplicate, value required
    
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    #   Type: String    | Configure  | String to 200, value required
    
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)
    #   Type: String or None  |    Configure |  String up to 200, prevent duplicate, value = None if default
    
    
    posts: Mapped[list[Post]] = relationship(   # Get posts belonging to user
    #   Type: List of posts
        back_populates="author",    # Connects to corresponding author
        cascade="all, delete-orphan"    # When user deleted, deletes all associated posts 
    )
    
    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    @property   # Lets you access the method as an attribute, user.image_path
    def image_path(self) -> str:
        if self.image_file:  # If image_file filled in
            # return f"/media/profile_pics/{self.image_file}"  # Return full directory of image file
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/profile_pics/{self.image_file}"
        
        return "/static/profile_pics/default.jpg"   # Else use default image
    
    
# Creates posts table in database

# post.title
# post.content
# post.user_id
# post.date_posted
# post.author

class Post(Base):
    __tablename__ = "posts"  # Name of table
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Type: Integer  | Configure  | Integer,  unique identifier, indexed
    
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    # Type: String   | Configure  | String up to 100, value required
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Type: String   |     Configure | Longer String, value required
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index = True)
    # Type: Integer  |     Configure | Refrences id column in users, refrence required, indexed
    
    date_posted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    # Type: Datetime |              Configure |   Value = time,         get current time in UTC
    
    likes: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Type: Interger |    Configure  | Interger, 0 likes default python side, 0 likes default database side
    
    author: Mapped[User] = relationship(back_populates="posts")
    # Type: User        |  Connects to user.posts
    
    
# Password Reset Token Model
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    user: Mapped[User] = relationship(back_populates="reset_tokens")
    