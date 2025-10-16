from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.models.chat import ChatRequest, ChatResponse
from app.controllers.chat_controller import chat_controller
from app.middleware.auth_middleware import get_optional_current_user
from app.models.chat import AdaptRequest, AdaptResponse, EscalateRequest, EscalateResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/chat', response_class=HTMLResponse, summary='Chatbot de ayuda')
async def chat_page(request: Request, current_user: dict | None = Depends(get_optional_current_user)):
    return templates.TemplateResponse('chat.html', {
        'request': request,
        'title': 'Chat de Ayuda',
        'user': current_user,
    })


@router.post('/api/chat/message', response_model=ChatResponse)
async def post_message(payload: ChatRequest, current_user: dict | None = Depends(get_optional_current_user)):
    resp = await chat_controller.handle_message(payload.message, current_user)
    # Normalize to ChatResponse fields
    return JSONResponse(content={
        'answer': resp.get('answer'),
        'resolved': bool(resp.get('resolved')),
        'source': resp.get('source'),
        'admin_email': resp.get('admin_email')
    })


@router.post('/api/chat/adapt', response_model=AdaptResponse)
async def post_adapt(payload: AdaptRequest, current_user: dict | None = Depends(get_optional_current_user)):
    resp = await chat_controller.adapt_snippet(payload.snippet, current_user)
    return JSONResponse(content={'adapted_answer': resp.get('adapted_answer')})


@router.post('/api/chat/escalate', response_model=EscalateResponse)
async def post_escalate(payload: EscalateRequest, current_user: dict | None = Depends(get_optional_current_user)):
    resp = await chat_controller.escalate(payload.original_message, current_user)
    return JSONResponse(content={'ticket_id': resp.get('ticket_id'), 'admin_email': resp.get('admin_email')})
