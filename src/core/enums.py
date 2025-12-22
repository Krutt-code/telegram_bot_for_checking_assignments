from enum import StrEnum


class AnswersStatusEnum(StrEnum):
    """Статусы ответов

    SENT - отправлен
    REVIEWED - проверен
    REJECTED - отклонен
    ACCEPTED - принят
    """

    SENT = "sent"
    REVIEWED = "reviewed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class MediaEnum(StrEnum):
    PHOTO = "photo"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    ETC = "etc"


class AnswerMediaTypeEnum(StrEnum):
    PHOTO = MediaEnum.PHOTO.value
    DOCUMENT = MediaEnum.DOCUMENT.value
    VIDEO = MediaEnum.VIDEO.value
    AUDIO = MediaEnum.AUDIO.value
    VOICE = MediaEnum.VOICE.value
    ETC = MediaEnum.ETC.value


class HomeworkMediaTypeEnum(StrEnum):
    PHOTO = MediaEnum.PHOTO.value
    DOCUMENT = MediaEnum.DOCUMENT.value
    VIDEO = MediaEnum.VIDEO.value


class UserRoleEnum(StrEnum):
    """
    Роль, выбранная пользователем в боте.
    """

    STUDENT = "student"
    TEACHER = "teacher"


class CommandsEnum(StrEnum):
    """
    Внутренние команды бота.

    Используется для связи хендлеров и кнопок.
    """

    START = "start"
    ROLE = "role"
    GENERAL_SETTINGS = "general_settings"
    HELP = "help"

    FULL_NAME_PANEL = "full_name_panel"
    SET_FULL_NAME = "set_full_name"

    STUDENT_ROLE = "student_role"
    STUDENT_HOMEWORKS = "student_homeworks"
    STUDENT_ANSWERS = "student_answers"
    STUDENT_GROUP = "student_group"

    TEACHER_ROLE = "teacher_role"
    TEACHER_HOMEWORKS = "teacher_homeworks"

    TEACHER_GROUPS = "teacher_groups"
    TEACHER_GROUP_CREATE = "teacher_group_create"
    TEACHER_GROUP_DELETE = "teacher_group_delete"
    TEACHER_GROUP_EDIT = "teacher_group_edit"
    TEACHER_GROUP_VIEW = "teacher_group_view"
    TEACHER_GROUP_ADD_STUDENT = "teacher_group_add_student"
    TEACHER_GROUP_REMOVE_STUDENT = "teacher_group_remove_student"
    TEACHER_GROUP_GET_LINK = "teacher_group_get_link"

    ADMIN_PANEL = "admin_panel"
    ADMIN_STUDENTS = "admin_students"
    ADMIN_GROUPS = "admin_groups"
    ADMIN_TEACHERS = "admin_teachers"

    BACK = "back"
    CANCEL = "cancel"


class ReplyKeyboardTypeEnum(StrEnum):
    """
    Типы готовых reply-клавиатур
    """

    ROLE = "role"
    GENERAL_SETTINGS = "general_settings"
    FULL_NAME_PANEL = "full_name_panel"
    ADMIN = "admin"
    ADMIN_PANEL = "admin_panel"
    ADMIN_STUDENTS = "admin_students"
    ADMIN_GROUPS = "admin_groups"
    ADMIN_TEACHERS = "admin_teachers"

    STUDENT = "student"
    STUDENT_HOMEWORKS = "student_homeworks"
    STUDENT_ANSWERS = "student_answers"

    TEACHER = "teacher"
    TEACHER_HOMEWORKS = "teacher_homeworks"
    TEACHER_GROUPS = "teacher_groups"
    TEACHER_GROUP_CREATE = "teacher_group_create"
    TEACHER_GROUP_VIEW = "teacher_group_view"


class InlineKeyboardTypeEnum(StrEnum):
    """
    Типы готовых inline-клавиатур
    """

    TEACHER_GROUPS_REVIEW = "teacher_groups_review"
    TEACHER_GROUP_STUDENTS_REVIEW = "teacher_group_students_review"
    STUDENT_GROUP_EXIT = "student_group_exit"
    STUDENT_HOMEWORK_REVIEW = "student_homework_review"
