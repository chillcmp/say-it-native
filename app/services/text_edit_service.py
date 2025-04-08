from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.logger import logger
from app.models import TextEdit, UsageLog
from app.services.text_editors import TextEditor


def run_text_edit(user_id: int, text: str, editor: TextEditor, db: Session) -> dict:
    result, num_tokens = editor.edit(text)

    text_edit = TextEdit(
        user_id=user_id,
        input_text=text,
        output_text=result,
        model_used='hf'
    )

    usage_log = UsageLog(
        user_id=user_id,
        tokens_used=num_tokens
    )

    try:
        db.add(text_edit)
        db.add(usage_log)
        db.commit()
        db.refresh(text_edit)
        db.refresh(usage_log)
        return {"original": text, "result": result, "tokens_used": num_tokens}
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
