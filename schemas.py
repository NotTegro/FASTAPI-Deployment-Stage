# Pydantic Schemas - Defines what data is accepted, checked, sends back.

from datetime import datetime   # Time

from pydantic import BaseModel, ConfigDict, Field, EmailStr
# BaseModel - Foundation of Pydantic Schemas
# ConfigDict - Configures how Pydantic handles a model
# Field - Adds validation rules, such as max length
# EmailStr - Validates an email value


# Foundation of User
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    # Type: String | minimum and maximum values
    
    email: EmailStr = Field(max_length=120)
    # Type: Email | maximum of 120 characters
    
    
# Create User
class UserCreate(UserBase):
    password: str = Field(min_length=8)

    
# Returns User username, id, image_file, image_path
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Allows to read user.username, etc.
    
    id: int                 # User's ID
    username: str           # User's Name
    image_file: str | None  # User's Image File
    image_path: str         # User's Image Path
    
    
# Includes user's email
class UserPrivate(UserPublic):
    email: EmailStr
    
    
# Change existing user, if some fields not changed, they are left out
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


# Shared Post Fields
class PostBase(BaseModel):
    # Title and content field
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    
    
# Inherits title and content, adds user_id to post
class PostCreate(PostBase):
    pass


# Editing Post
class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


# Returning Post
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)  # Sees data from test[0] to test.id

    id: int                 # Post's ID
    user_id: int            # User's ID
    date_posted: datetime   # Post's Date of Creation
    author: UserPublic      # Author's Information
    
    
class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    

# Password Reset Schemas    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)
    
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)
    
    
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    
    
    