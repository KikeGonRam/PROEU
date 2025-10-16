from fastapi import Request
from app.utils.llm_client import generate_answer
from app.config.database import get_database
from bson import ObjectId


class ChatController:
    async def handle_message(self, message: str, user: dict | None = None):
        # Use the mock LLM client for now
        resp = generate_answer(message, user)
        return resp

    async def adapt_snippet(self, snippet: str, user: dict | None = None):
        # very simple adapt: prepend contextual sentence
        name = None
        if user:
            name = user.get('nombre') or user.get('email')
        prefix = f"Hola {name}, aquí lo adapto a tu caso: \n" if name else "Aquí lo adapto a tu caso:\n"
        adapted = prefix + snippet
        return {'adapted_answer': adapted}

    async def escalate(self, original_message: str, user: dict | None = None):
        # Create a ticket in MongoDB 'tickets' collection
        db = get_database()
        tickets = db.tickets
        ticket = {
            'message': original_message,
            'user': user or {},
            'status': 'open',
            'created_at': __import__('datetime').datetime.utcnow()
        }
        res = tickets.insert_one(ticket)
        ticket_id = str(res.inserted_id)
        admin_email = 'admin@institucion.edu.mx'
        return {'ticket_id': ticket_id, 'admin_email': admin_email}


chat_controller = ChatController()
