from flask import request, session
from flask_restful import Resource

from ..extensions import db
from ..models import Note


def non_empty(value):
    return isinstance(value, str) and bool(value.strip())


class Notes(Resource):
    def get(self):
        page = max(request.args.get("page", 1, type=int), 1)
        per_page = min(max(request.args.get("per_page", 5, type=int), 1), 100)
        pagination = (
            Note.query.filter_by(user_id=session["user_id"])
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return {
            "notes": [note.to_dict() for note in pagination.items],
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        data = request.get_json() or {}
        if not non_empty(data.get("title")) or not non_empty(data.get("content")):
            return {"errors": ["Title and content are required."]}, 422

        note = Note(
            title=data["title"].strip(),
            content=data["content"].strip(),
            user_id=session["user_id"],
        )
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteById(Resource):
    def patch(self, id):
        note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
        if not note:
            return {"errors": ["Note not found."]}, 404

        data = request.get_json() or {}
        for field in ("title", "content"):
            if field in data:
                if not non_empty(data[field]):
                    return {"errors": [f"{field} cannot be empty."]}, 422
                setattr(note, field, data[field].strip())
        db.session.commit()
        return note.to_dict(), 200

    def delete(self, id):
        note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
        if not note:
            return {"errors": ["Note not found."]}, 404
        db.session.delete(note)
        db.session.commit()
        return {}, 204


def register_note_resources(api):
    api.add_resource(Notes, "/notes", endpoint="notes")
    api.add_resource(NoteById, "/notes/<int:id>", endpoint="note_by_id")
