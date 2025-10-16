"""
Mock LLM client / FAQ responder.
Replace with real provider integration (OpenAI, Azure, or local LLM) in production.
"""
from typing import Optional
import unicodedata
import re
import os
from app.utils.knowledge import search_docs


FAQ = {
    "¿cómo creo una solicitud?": "Para crear una solicitud, ve a 'Nueva Solicitud' y completa el formulario con los datos requeridos.",
    "¿cómo subo un comprobante?": "En la vista de la solicitud aprobada, usa 'Subir comprobante' y añade el archivo PDF o imagen.",
    "¿qué roles existen?": "Los roles disponibles son: solicitante, aprobador, pagador y admin.",
    "mis solicitudes": "Puedes ver tus solicitudes en la sección 'Mis Solicitudes' o en /requests. Filtra por estado para ver pendientes, aprobadas o pagadas.",
    "cómo funciona el sistema": "Este sistema permite a los solicitantes crear y seguir solicitudes de pago, a los aprobadores revisar y aprobar, y a los pagadores marcar como pagadas y subir comprobantes. Usa el menú 'Solicitudes' para ver y crear solicitudes.",
}


def answer_faq(question: str) -> Optional[str]:
    q = normalize_text(question)
    # try exact normalized match
    for k, v in FAQ.items():
        if normalize_text(k) == q:
            return v
    # try substring match
    for k, v in FAQ.items():
        if normalize_text(k) in q:
            return v
    return None


def normalize_text(s: str) -> str:
    if not s:
        return ''
    # lower
    s = s.lower()
    # remove accents
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    # remove punctuation (Unicode-aware)
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE)
    # collapse spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def generate_answer(message: str, user: dict | None = None) -> dict:
    """
    Very small heuristic responder:
    - If message matches known FAQ, return answer with resolved=True
    - Otherwise, return resolved=False and suggest escalation to admin
    """
    ans = answer_faq(message)
    if ans:
        return {"answer": ans, "resolved": True, "source": "faq"}

    # Try to find matching snippets in local docs/README/templates to answer basic questions
    try:
        hits = search_docs(message, top_k=3)
        if hits:
            # build a short, friendly summary from the best hit(s)
            best = hits[0]
            snippet = best[1]
            # clean snippet
            s = re.sub(r'\*\*|__|\*', '', snippet)
            s = re.sub(r'\s+', ' ', s).strip()
            if len(s) > 250:
                s = s[:250].rsplit(' ', 1)[0] + '...'

            answer_text = (
                "Encontré esto en la documentación y creo que responde tu pregunta:\n\n"
                f"{s}\n\n"
                "¿Quieres que lo adapte específicamente a tu caso o prefieres que lo escale al administrador?"
            )

            return {
                'answer': answer_text,
                'resolved': True,
                'source': 'docs',
            }
    except Exception:
        # if doc search fails for any reason, ignore and continue
        pass

    # If user is a solicitante we can answer some role-specific intents
    if user and user.get('role') == 'solicitante':
        q = normalize_text(message)
        if 'mis solicitudes' in q or 'ver mis solicitudes' in q or 'mis solicitud' in q:
            return {
                'answer': "Visita /requests para ver tus solicitudes. Puedes filtrar por estado (pendiente, aprobada, pagada).",
                'resolved': True,
                'source': 'internal',
            }
        if 'estado' in q and 'solicitud' in q:
            # If we had user's id we could provide direct status; offer instructions instead
            return {
                'answer': "Para ver el estado de una solicitud específica, abre la solicitud desde /requests y consulta la sección 'Estado'. También puedes usar el ID de solicitud en la búsqueda.",
                'resolved': True,
                'source': 'internal',
            }
        # recognize different forms like 'crea', 'crear', 'como crear', etc.
        if (('crear' in q or 'crea' in q or 'como' in q or 'hacer' in q) and 'solicitud' in q) or ('nueva solicitud' in q):
            return {
                'answer': "Para crear una nueva solicitud, ve a 'Nueva Solicitud' o a /solicitud-estandar/nueva y completa los campos. Asegúrate de adjuntar documentos si son requeridos.",
                'resolved': True,
                'source': 'internal',
            }

    # not found: suggest contacting admin. If user provided, include admin email placeholder
    admin_email = None
    if user and user.get("role") == "admin":
        admin_email = user.get("email")
    else:
        # fallback: global admin email (could be read from config)
        admin_email = "admin@institucion.edu.mx"

    return {
        "answer": "No he podido resolver tu duda automáticamente. ¿Quieres que lo escale al administrador?",
        "resolved": False,
        "source": None,
        "admin_email": admin_email,
    }
