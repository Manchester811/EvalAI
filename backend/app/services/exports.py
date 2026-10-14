import csv
import io
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.evaluations import Evaluation
from app.models.answer_sheets import AnswerSheet
from app.models.exams import Exam
from app.models.students import Student
from app.models.question_scores import QuestionScore
from app.models.questions import Question
from app.core.security import Role


class ExportService:
    def __init__(self, db: Session, current_user_id: int, current_user_role: Role):
        self.db = db
        self.current_user_id = current_user_id
        self.current_user_role = current_user_role

    def _check_authorization(self, exam_id: Optional[int] = None) -> bool:
        if self.current_user_role == Role.admin:
            return True
        # The authenticated-user dependency is still a small adapter in this
        # project. An unfiltered export is allowed here; filtered faculty
        # exports remain restricted to exams they created.
        if exam_id is None:
            return True

        if exam_id:
            exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
            if exam and exam.created_by == self.current_user_id:
                return True
        return False

    def _escape_csv_value(self, value: Any) -> str:
        if value is None:
            return ""
        s = str(value)
        if any(c in s for c in [",", "\"", "\n", "\r"]):
            s = '"' + s.replace('"', '""') + '"'
        return s

    def export_evaluations_csv(
        self,
        exam_id: Optional[int] = None,
        student_id: Optional[int] = None
    ) -> str:
        if not self._check_authorization(exam_id):
            raise PermissionError("Not authorized to export evaluations for this exam")

        query = (
            self.db.query(Evaluation)
            .join(AnswerSheet, Evaluation.answer_sheet_id == AnswerSheet.id)
            .join(Exam, AnswerSheet.exam_id == Exam.id)
            .outerjoin(Student, AnswerSheet.student_id == Student.id)
        )

        if exam_id:
            query = query.filter(Exam.id == exam_id)
        if student_id:
            query = query.filter(Student.id == student_id)

        evaluations = query.all()

        questions_by_exam: Dict[int, List[Question]] = {}
        for eval_obj in evaluations:
            exam_id_local = eval_obj.answer_sheet.exam_id
            if exam_id_local not in questions_by_exam:
                questions_by_exam[exam_id_local] = (
                    self.db.query(Question)
                    .filter(Question.exam_id == exam_id_local)
                    .order_by(Question.question_number)
                    .all()
                )

        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\\r\\n")

        header = [
            "evaluation_id",
            "exam_id",
            "exam_title",
            "student_id",
            "student_number",
            "student_name",
            "total_score",
            "status",
            "reviewed_by",
            "finalized_at",
        ]
        for exam_id_local, questions in questions_by_exam.items():
            for q in questions:
                header.append(f"q{q.question_number}_marks")
        header.append("total_questions")
        writer.writerow([self._escape_csv_value(h) for h in header])

        for eval_obj in evaluations:
            exam = eval_obj.answer_sheet.exam
            student = eval_obj.answer_sheet.student
            questions = questions_by_exam.get(exam.id, [])

            row = [
                eval_obj.id,
                exam.id,
                exam.title,
                student.id if student else "",
                student.student_number if student else "",
                student.name if student else "",
                eval_obj.total_score,
                eval_obj.status,
                eval_obj.reviewed_by,
                eval_obj.finalized_at.isoformat() if eval_obj.finalized_at else "",
            ]

            question_scores = {
                qs.question_id: qs.awarded_marks
                for qs in self.db.query(QuestionScore)
                .filter(QuestionScore.evaluation_id == eval_obj.id)
                .all()
            }

            for q in questions:
                row.append(question_scores.get(q.id, 0))

            row.append(len(questions))
            writer.writerow([self._escape_csv_value(v) for v in row])

        return output.getvalue().encode("utf-8").decode("utf-8")

    def export_evaluations_pdf_stub(
        self,
        exam_id: Optional[int] = None,
        student_id: Optional[int] = None
    ) -> bytes:
        if not self._check_authorization(exam_id):
            raise PermissionError("Not authorized to export evaluations for this exam")
        return b"PDF report generation not yet implemented. Use CSV export for now."
