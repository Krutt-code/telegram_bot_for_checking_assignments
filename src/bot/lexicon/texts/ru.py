from enum import StrEnum


class TextsRU(StrEnum):
    # Parser-mod: HTML

    HELLO = (
        "👋 Привет! Этот бот нужен для распределения заданий между студентами и преподавателями.\n\n"
        "Выберите свою роль, нажав на соответствующую кнопку.\n\n"
        "Если захотите переключиться на другую роль, используйте команду /start или /role"
    )
    HELLO_STUDENT = (
        "Это меню студента. Здесь вы можете посмотреть свои задания и ответы."
    )
    HELLO_TEACHER = (
        "Это меню преподавателя. Здесь вы можете посмотреть свои задания и группы."
    )
    HELP = "Пока нет"

    SELECT_ROLE = "Выберите свою роль, нажав на соответствующую кнопку."
    SELECT_ACTION = "Выберите действие, нажав на соответствующую кнопку."

    FULL_NAME_NOW = "Зарегистрированное ФИО: {full_name}"
    FULL_NAME_ENTER = (
        "Пожалуйста, введите ваше ФИО."
        "\nЕго будут видеть преподователи и студенты."
        "\n\nПример: Иванов Иван Иванович"
    )
    FULL_NAME_ERROR = "Ошибка добавления ФИО. Оно должно содержать хотя бы 2 слова."
    FULL_NAME_SUCCESS = "ФИО успешно сохранено."
    FULL_NAME_NOT_CHANGED = "ФИО не изменилось."
    FULL_NAME_REQUIRED = "Для продолжения работы заполните ФИО."

    HELLO_ADMIN_PANEL = "Добро пожаловать в админ-панель"

    BACK_OK = "⬅️ Возвращаюсь назад"
    BACK_NOT_POSSIBLE = "❌ Назад неполучится. Используйте /start"

    CANCEL = "Отмена"

    TRY_AGAIN = "Попробуйте еще раз"

    # --- Teacher: groups ---
    TEACHER_GROUPS_TITLE = "<b>Ваши группы</b>"
    TEACHER_GROUPS_EMPTY = "<b>Ваши группы</b>\n\nПока нет закреплённых за вами групп."
    TEACHER_NOT_FOUND = "Не удалось найти запись преподавателя. Попробуйте заново выбрать роль через /role."
    TEACHER_GROUP_CREATE_TITLE = (
        "Пожалуйста, введите название новой группы."
        "\n\nЭто может быть как учебная группа, так и группа для самостоятельной работы."
    )
    TEACHER_GROUP_CREATE_INVALID_NAME = (
        "❌ Некорректное название группы. Введите от 1 до 255 символов."
    )
    TEACHER_GROUP_CREATE_DUPLICATE_NAME = (
        "❌ У вас уже есть группа с таким названием. Введите другое."
    )
    TEACHER_GROUP_CREATE_FAILED = "❌ Не удалось создать группу. Попробуйте ещё раз."
    TEACHER_GROUP_CREATE_SUCCESS = "✅ Группа «{name}» создана и привязана к вам."

    # --- Teacher: group view / students ---
    TEACHER_GROUP_STUDENTS_TITLE = (
        "<b>Студенты группы</b>\n\n{group_name}\n\n{students_list}"
    )
    TEACHER_GROUP_STUDENTS_EMPTY = "В этой группе пока нет студентов."
    TEACHER_GROUP_OPEN_FAILED = (
        "❌ Не удалось открыть группу. Возможно, она была удалена."
    )

    # --- Teacher: group edit ---
    TEACHER_GROUP_EDIT_PROMPT = (
        'Текущее название: "{group_name}"\n\nВведите новое название группы'
    )
    TEACHER_GROUP_EDIT_SUCCESS = "✅ Название группы обновлено."
    TEACHER_GROUP_EDIT_DUPLICATE_NAME = (
        "❌ У вас уже есть группа с таким названием. Введите другое."
    )
    TEACHER_GROUP_EDIT_INVALID_NAME = (
        "❌ Некорректное название группы. Введите от 1 до 255 символов."
    )

    # --- Teacher: group delete ---
    TEACHER_GROUP_DELETE_CONFIRM = (
        'Вы уверены что хотите удалить группу "{group_name}"?\n\n'
        "Для удаления пришлите название группы"
    )
    TEACHER_GROUP_DELETE_SUCCESS = "✅ Группа удалена."
    TEACHER_GROUP_DELETE_NAME_MISMATCH = (
        "❌ Название не совпало. Для удаления пришлите точное название группы."
    )

    # --- Teacher: get link ---
    TEACHER_GROUP_GET_LINK = (
        "Ссылка для добавления студентов в группу.\n\n"
        "Нажмите кнопку ниже, чтобы скопировать."
    )
    TEACHER_GROUP_GET_LINK_BUTTON = "Скопировать ссылку"

    # --- Teacher: remove student from group ---
    TEACHER_GROUP_STUDENT_REMOVE_CONFIRM_ALERT = (
        "Удалить студента из группы?\n\nНажмите на кнопку ещё раз, чтобы подтвердить."
    )
    TEACHER_GROUP_STUDENT_REMOVE_SUCCESS_ALERT = "Студент удалён из группы."
    TEACHER_GROUP_STUDENT_REMOVE_FAILED_ALERT = (
        "Не удалось удалить студента (возможно, он уже не в этой группе)."
    )

    # --- Teacher: grading ---
    TEACHER_GRADING_CHECK_BUTTON = "✅ Проверить"
    TEACHER_GRADING_REVIEWED_BUTTON = "📋 Оцененные"
    TEACHER_GRADING_ANSWER_VIEW = (
        "<b>Студент:</b> {student_name}\n"
        "<b>Группа:</b> {group_name}\n\n"
        "<b>Ответ:</b>\n{answer_text}\n\n"
        "<b>Отправлено:</b> {sent_at}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "{grade_status}\n"
        "{comment_status}"
    )
    TEACHER_GRADING_ANSWER_NO_TEXT = "<i>Текстовый ответ отсутствует</i>"
    TEACHER_GRADING_REVIEWED_VIEW = (
        "<b>Студент:</b> {student_name}\n"
        "<b>Группа:</b> {group_name}\n\n"
        "<b>Ответ:</b>\n{answer_text}\n\n"
        "<b>Оценка:</b> {grade}/100\n"
        "<b>Комментарий:</b> {comment}\n\n"
        "<b>Проверено:</b> {checked_at}"
    )
    TEACHER_GRADING_NO_COMMENT = "<i>Без комментария</i>"
    TEACHER_GRADING_GRADE_STATUS_SET = "✅ <b>Оценка:</b> {grade}/100"
    TEACHER_GRADING_GRADE_STATUS_NOT_SET = "❌ <b>Оценка:</b> не выставлена"
    TEACHER_GRADING_COMMENT_STATUS_SET = "✅ <b>Комментарий:</b> {comment_preview}"
    TEACHER_GRADING_COMMENT_STATUS_NOT_SET = "❌ <b>Комментарий:</b> не добавлен"
    TEACHER_GRADING_SET_GRADE_BUTTON = "✏️ Дать оценку"
    TEACHER_GRADING_SET_COMMENT_BUTTON = "💬 Комментировать"
    TEACHER_GRADING_SEND_BUTTON = "📤 Отправить"
    TEACHER_GRADING_SENT_BUTTON = "✅ Отправлено"
    TEACHER_GRADING_CLEAR_BUTTON = "🗑️ Очистить"
    TEACHER_GRADING_EDIT_GRADE_BUTTON = "✏️ Изменить оценку"
    TEACHER_GRADING_EDIT_COMMENT_BUTTON = "💬 Изменить комментарий"
    TEACHER_GRADING_ENTER_GRADE = "Введите оценку от 0 до 100 баллов."
    TEACHER_GRADING_INVALID_GRADE = "❌ Некорректная оценка. Введите число от 0 до 100."
    TEACHER_GRADING_GRADE_SET = "✅ Оценка установлена: {grade}/100"
    TEACHER_GRADING_ENTER_COMMENT = (
        "Введите комментарий к ответу студента.\n\n"
        "Или нажмите кнопку «Пропустить», если комментарий не нужен."
    )
    TEACHER_GRADING_COMMENT_SET = "✅ Комментарий добавлен"
    TEACHER_GRADING_COMMENT_SKIPPED = "Комментарий пропущен"
    TEACHER_GRADING_COMMENT_SKIP = "Пропустить"
    TEACHER_GRADING_SEND_CONFIRM = (
        "Отправить оценку студенту?\n\n"
        "<b>Оценка:</b> {grade}/100\n"
        "<b>Комментарий:</b> {comment}"
    )
    TEACHER_GRADING_SEND_SUCCESS = "✅ Оценка отправлена студенту"
    TEACHER_GRADING_SEND_ERROR = "Сначала установите оценку"
    TEACHER_GRADING_ALREADY_SENT = "Оценка уже отправлена, если хотите изменить, используйте кнопку редактирования уже отправленных оценок."
    TEACHER_GRADING_CLEARED = "🗑️ Оценка и комментарий очищены"
    TEACHER_GRADING_ANSWER_NOT_FOUND = "Ответ не найден"
    TEACHER_GRADING_NO_ANSWERS_TO_CHECK = "Нет ответов для проверки"
    TEACHER_GRADING_NO_REVIEWED_ANSWERS = "Нет проверенных ответов"
    TEACHER_GRADING_ALL_CHECKED = "✅ Все ответы на это задание проверены!"
    TEACHER_GRADING_STUDENT_NOTIFICATION = (
        "📝 Ваш ответ на задание «{homework_title}» проверен!\n\n"
        "<b>Оценка:</b> {grade}/100\n"
        "<b>Комментарий:</b> {comment}"
    )
    TEACHER_GRADING_EDIT_NOTIFICATION = (
        "📝 Оценка за задание «{homework_title}» изменена!\n\n"
        "<b>Новая оценка:</b> {grade}/100\n"
        "<b>Комментарий:</b> {comment}"
    )
    TEACHER_GRADING_COMMENT_EDIT_NOTIFICATION = (
        "📝 Комментарий к заданию «{homework_title}» изменён!\n\n"
        "<b>Оценка:</b> {grade}/100\n"
        "<b>Новый комментарий:</b> {comment}"
    )
    TEACHER_GRADING_COMMENT_UPDATED = "✅ Комментарий обновлён"

    # --- Student: join group by invite ---
    STUDENT_JOIN_GROUP_INVALID = "❌ Ссылка недействительна или группа не найдена."
    STUDENT_JOIN_GROUP_SUCCESS = (
        '✅ Вы добавлены в группу "{group_name}"\n' "Преподаватель: {teacher_full_name}"
    )

    # --- Student: group ---
    STUDENT_GROUP_NOT_FOUND = "❌ Группа не найдена."
    STUDENT_GROUP_INFO = (
        "Вы в группе «{group_name}». Преподаватель: {teacher_full_name}"
    )
    STUDENT_GROUP_EXIT = "Выйти из группы"
    STUDENT_GROUP_EXIT_CONFIRM = "Вы уверены что хотите выйти из группы?"
    STUDENT_GROUP_EXIT_SUCCESS = "Вы вышли из группы."
    STUDENT_GROUP_EXIT_FAILED = "Не удалось выйти из группы."

    # --- Student: homeworks ---
    STUDENT_HOMEWORKS_EMPTY = "<b>Задания</b>\n\nПока нет заданий для вашей группы."
    STUDENT_HOMEWORK_ANSWER_BUTTON = "Ответить"
    STUDENT_HOMEWORK_ANSWER_BUTTON_NOOP = "Время для ответа истекло"
    STUDENT_HOMEWORK_START_AT_LINE = "<b>Выдано:</b> {start_at}\n"
    STUDENT_HOMEWORK_TEACHER_LINE = "<b>Преподаватель:</b> {teacher_full_name}\n"
    STUDENT_HOMEWORK_ANSWER_PROMPT = (
        "<b>Ответ на задание</b>\n\n"
        "Отправьте ваш ответ <b>текстом</b> одним сообщением."
    )
    STUDENT_HOMEWORK_ANSWER_TEXT_ONLY = (
        "Пожалуйста, отправьте ответ текстовым сообщением."
    )
    STUDENT_HOMEWORK_ANSWER_EMPTY = "Ответ пустой. Отправьте текст."
    STUDENT_HOMEWORK_ANSWER_SENT = "✅ Ответ отправлен."
    STUDENT_HOMEWORK_ANSWER_DEADLINE_PASSED = (
        "❌ Срок сдачи истёк. Ответить уже нельзя."
    )
    STUDENT_HOMEWORK_VIEW = (
        "<b>Задание</b>\n\n"
        "<b>Тема:</b> {title}\n"
        "<b>Срок сдачи:</b> {end_at}\n"
        "{start_at_line}"
        "{teacher_line}"
        "\n<b>Описание:</b>\n{text}"
    )

    # --- Student: answers ---
    STUDENT_ANSWERS_EMPTY = "<b>Ответы</b>\n\nПока нет отправленных ответов."
    STUDENT_ANSWER_STATUS_SENT = "Отправлено"
    STUDENT_ANSWER_STATUS_REVIEWED = "Проверено"
    STUDENT_ANSWER_STATUS_REJECTED = "Отклонено"
    STUDENT_ANSWER_STATUS_ACCEPTED = "Принято"
    STUDENT_ANSWER_VIEW = (
        "<b>Ответ</b>\n\n"
        "<b>Задание:</b> {homework_title}\n"
        "<b>Отправлено:</b> {sent_at}\n"
        "<b>Статус:</b> {status}\n"
        "{grade_line}"
        "{comment_line}"
        "\n<b>Ваш ответ:</b>\n{student_answer}"
    )

    # --- Teacher: homeworks ---
    TEACHER_HOMEWORKS_EMPTY = "<b>Задания</b>\n\nПока нет созданных заданий."
    TEACHER_HOMEWORK_VIEW = (
        "<b>Задание</b>\n\n"
        "<b>Тема:</b> {title}\n"
        "<b>Выдано:</b> {start_at}\n"
        "<b>Срок сдачи:</b> {end_at}\n\n"
        "<b>Группы:</b> {groups}\n"
        "<b>Ответов:</b> {answers_count}\n\n"
        "<b>Описание:</b>\n{text}"
    )
    TEACHER_HOMEWORK_GROUPS_EMPTY = "—"
    TEACHER_HOMEWORK_EDIT_BUTTON = "Редактировать"
    TEACHER_HOMEWORK_DELETE_BUTTON = "Удалить"
    TEACHER_HOMEWORK_DELETE_CONFIRM_ALERT = (
        "Удалить задание?\n\nНажмите на кнопку ещё раз, чтобы подтвердить."
    )
    TEACHER_HOMEWORK_DELETE_SUCCESS_ALERT = "Задание удалено."
    TEACHER_HOMEWORK_DELETED = "✅ Задание удалено ({deleted_at})."

    TEACHER_HOMEWORK_EDIT_TITLE = "Название"
    TEACHER_HOMEWORK_EDIT_TEXT = "Текст"
    TEACHER_HOMEWORK_EDIT_FILES = "Файлы"
    TEACHER_HOMEWORK_EDIT_GROUPS = "Группы"
    TEACHER_HOMEWORK_EDIT_BACK = "Назад"
    TEACHER_HOMEWORK_EDIT_TITLE_PROMPT = "Введите новое название задания."
    TEACHER_HOMEWORK_EDIT_TITLE_EMPTY = "Название пустое. Введите текст."
    TEACHER_HOMEWORK_EDIT_TEXT_PROMPT = "Введите новый текст задания."
    TEACHER_HOMEWORK_EDIT_TEXT_EMPTY = "Текст пустой. Введите текст."
    TEACHER_HOMEWORK_EDIT_SUCCESS = "✅ Изменения сохранены."
    TEACHER_HOMEWORK_EDIT_FILES_PROMPT = (
        "Пришлите новые файлы (фото/документы) для задания.\n\n"
        "Старые файлы будут заменены.\n"
        "Когда закончите — отправьте /done"
    )
    TEACHER_HOMEWORK_EDIT_FILES_ADDED = (
        "✅ Файл добавлен. Всего файлов: {count}. Добавьте ещё или /done."
    )
    TEACHER_HOMEWORK_EDIT_GROUPS_PROMPT = (
        "<b>Выберите группы</b>\n\nНажимайте на группы для выбора."
    )
    TEACHER_HOMEWORK_EDIT_GROUPS_EMPTY = "Выберите хотя бы одну группу."

    TEACHER_HOMEWORK_CREATE_TITLE_PROMPT = "Введите название нового задания."
    TEACHER_HOMEWORK_CREATE_TITLE_EMPTY = "Название пустое. Введите текст."
    TEACHER_HOMEWORK_CREATE_TEXT_PROMPT = "Введите описание задания."
    TEACHER_HOMEWORK_CREATE_TEXT_EMPTY = "Описание пустое. Введите текст."
    TEACHER_HOMEWORK_CREATE_DEADLINE_PROMPT = (
        "Введите срок сдачи.\n\nФормат: <b>ДД.ММ.ГГГГ ЧЧ:ММ</b>\n"
        "Например: 31.12.2025 23:59"
    )
    TEACHER_HOMEWORK_CREATE_DEADLINE_INVALID = (
        "❌ Некорректная дата. Попробуйте ещё раз."
    )
    TEACHER_HOMEWORK_CREATE_DEADLINE_PAST = "❌ Срок сдачи должен быть в будущем."
    TEACHER_HOMEWORK_CREATE_FILES_PROMPT = (
        "Пришлите фото и/или документы к заданию.\n\n"
        "Отправляйте по одному сообщению.\n"
        "Когда закончите — отправьте команду /done\n\n"
        "Если файлов нет — тоже отправьте /done"
    )
    TEACHER_HOMEWORK_CREATE_FILES_PHOTO_ONLY = "Пока поддерживаются фото/документы (и опционально видео). Пришлите файл или /done."
    TEACHER_HOMEWORK_CREATE_FILES_ADDED = (
        "✅ Файл добавлен. Всего файлов: {count}. Добавьте ещё или /done."
    )
    TEACHER_HOMEWORK_CREATE_GROUPS_PROMPT = (
        "<b>Выберите группы</b>\n\nНажимайте на группы для выбора."
    )
    TEACHER_HOMEWORK_CREATE_GROUPS_EMPTY = "Выберите хотя бы одну группу."
    TEACHER_HOMEWORK_GROUP_SELECTED_PREFIX = "✅"
    TEACHER_HOMEWORK_GROUP_UNSELECTED_PREFIX = "☑"
    TEACHER_HOMEWORK_GROUPS_DONE_BUTTON = "Готово"
    TEACHER_HOMEWORK_PREVIEW = (
        "<b>Предпросмотр</b>\n\n"
        "<b>Тема:</b> {title}\n"
        "<b>Срок сдачи:</b> {end_at}\n"
        "<b>Групп:</b> {groups_count}\n\n"
        "<b>Описание:</b>\n{text}\n\n"
        "Подтвердить создание?"
    )
    TEACHER_HOMEWORK_CONFIRM_CREATE_BUTTON = "Подтвердить"
    TEACHER_HOMEWORK_CANCEL_CREATE_BUTTON = "Отмена"
    TEACHER_HOMEWORK_CREATE_SUCCESS = "✅ Задание создано."
    TEACHER_HOMEWORK_NEW_NOTIFICATION = (
        "📚 Новое задание!\n\n"
        "<b>Тема:</b> {title}\n"
        "<b>Срок сдачи:</b> {end_at}\n"
        "<b>Преподаватель:</b> {teacher_full_name}\n\n"
        "<b>Описание:</b>\n{text}"
    )
