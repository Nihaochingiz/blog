from fastapi import APIRouter, status, HTTPException, Depends
from blog.domains import Admin
from blog.schemas import (
    GetArticlesModel,
    CreateArticleModel,
    LoginModel,
    GetArticleModel,
    ErrorModel,
)
from blog import services
from blog.repositories import ShelveArticlesRepository, MemoryUsersRepository

router = APIRouter()

def get_articles_repository():
    return ShelveArticlesRepository()

def get_users_repository():
    return MemoryUsersRepository()

@router.get("/articles", response_model=GetArticlesModel)
def get_articles(
    articles_repo: ShelveArticlesRepository = Depends(get_articles_repository)
) -> GetArticlesModel:
    articles = services.get_articles(articles_repository=articles_repo)
    return GetArticlesModel(
        items=[
            GetArticleModel(id=article.id, title=article.title, content=article.content)
            for article in articles
        ]
    )

@router.post(
    "/articles",
    response_model=GetArticleModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorModel, "description": "Authentication failed"},
        403: {"model": ErrorModel, "description": "Not enough permissions"}
    },
)
def create_article(
    article: CreateArticleModel, 
    credentials: LoginModel,
    articles_repo: ShelveArticlesRepository = Depends(get_articles_repository),
    users_repo: MemoryUsersRepository = Depends(get_users_repository)
) -> GetArticleModel:
    current_user = services.login(
        username=credentials.username,
        password=credentials.password,
        users_repository=users_repo,
    )
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized user"
        )
    
    if not isinstance(current_user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Forbidden resource"
        )

    new_article = services.create_article(
        title=article.title,
        content=article.content,
        articles_repository=articles_repo,
    )

    return GetArticleModel(
        id=new_article.id, 
        title=new_article.title, 
        content=new_article.content
    )