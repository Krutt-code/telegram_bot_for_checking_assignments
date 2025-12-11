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
