from typing import Any

from julca_bakalarka.db.models.question_model import Question


class QuestionDAO:
    """Data access object for the Question table."""

    async def create(
        self,
        text: str,
        media_filename: str,
        order: int,
        *,
        is_practice: bool = False,
    ) -> Question:
        """Create a new question."""
        question = Question(
            text=text,
            media_filename=media_filename,
            order=order,
            is_practice=is_practice,
        )
        await question.save()
        return question

    async def update(self, question_id: int, **kwargs: Any) -> None:
        """Update a question by ID."""
        await Question.update(kwargs).where(  # type: ignore[arg-type]
            Question.id == question_id,  # type: ignore[attr-defined]
        )

    async def delete(self, question_id: int) -> None:
        """Delete a question by ID."""
        await Question.delete().where(
            Question.id == question_id,  # type: ignore[attr-defined]
        )

    async def get_all_ordered(self) -> list[dict[str, Any]]:
        """Get all questions ordered by the order field."""
        return await (
            Question.select()
            .order_by(Question.is_practice, ascending=False)
            .order_by(Question.order)
        )

    async def get_by_id(self, question_id: int) -> dict[str, Any] | None:
        """Get a single question by ID."""
        results = await Question.select().where(
            Question.id == question_id,  # type: ignore[attr-defined]
        )
        return results[0] if results else None

    async def get_practice_questions(self) -> list[dict[str, Any]]:
        """Get all practice/control questions."""
        return await (
            Question.select()
            .where(Question.is_practice.eq(True))
            .order_by(Question.order)
        )

    async def get_survey_questions(self) -> list[dict[str, Any]]:
        """Get all non-practice questions."""
        return await (
            Question.select()
            .where(Question.is_practice.eq(False))
            .order_by(Question.order)
        )

    async def get_max_order(self) -> int:
        """Get the maximum order value, or 0 if no questions exist."""
        result = await Question.raw('SELECT MAX("order") as max_order FROM question')
        if result and result[0]["max_order"] is not None:
            return result[0]["max_order"]
        return 0
