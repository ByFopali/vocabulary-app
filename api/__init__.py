from fastapi import APIRouter

from api.router.grammar_element_router import router as grammar_element_router
from auth.router import router as auth_router
from api.router.language_router import router as language_router
from api.router.topic_router import router as topic_router
from api.router.word_router import router as word_router

main_api_router = APIRouter()

main_api_router.include_router(grammar_element_router)
main_api_router.include_router(auth_router)
main_api_router.include_router(language_router)
main_api_router.include_router(topic_router)
main_api_router.include_router(word_router)
