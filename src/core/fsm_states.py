from aiogram.fsm.state import State, StatesGroup


class FullNameStates(StatesGroup):
    waiting_for_full_name = State()


class TeacherGroupCreateStates(StatesGroup):
    waiting_for_group_name = State()


class TeacherGroupEditStates(StatesGroup):
    waiting_for_new_name = State()


class TeacherGroupDeleteStates(StatesGroup):
    waiting_for_confirm_name = State()


class StudentHomeworkAnswerStates(StatesGroup):
    waiting_for_text = State()


class TeacherHomeworkCreateStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_text = State()
    waiting_for_deadline = State()
    waiting_for_files = State()
    selecting_groups = State()
    confirming = State()


class TeacherHomeworkEditStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_text = State()
    waiting_for_files = State()
    selecting_groups = State()


class TeacherAnswerGradingStates(StatesGroup):
    """Состояния для выставления оценки и комментария"""

    waiting_for_grade = State()
    waiting_for_comment = State()
    editing_grade = State()
    editing_comment = State()  # Редактирование комментария


class AdminBanUserStates(StatesGroup):
    """Состояния для блокировки пользователя"""

    waiting_for_user_id = State()
    waiting_for_reason = State()


class AdminUnbanUserStates(StatesGroup):
    """Состояния для разблокировки пользователя"""

    waiting_for_user_id = State()
