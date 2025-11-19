-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Хост: localhost:3306
-- Время создания: Ноя 19 2025 г., 01:14
-- Версия сервера: 8.0.43-0ubuntu0.24.04.2
-- Версия PHP: 8.3.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `bot`
--

-- --------------------------------------------------------

--
-- Структура таблицы `admins`
--

CREATE TABLE `admins` (
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `answers`
--

CREATE TABLE `answers` (
  `answer_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `student_id` int NOT NULL,
  `text` text,
  `status` enum('sent','reviewed','rejected','accepted') NOT NULL COMMENT 'Статусы проверки преподавателя',
  `grade` tinyint DEFAULT NULL,
  `teacher_comment` text,
  `sent_at` datetime NOT NULL,
  `checked_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Ответы студентов на задания с оценкой преподователя';

-- --------------------------------------------------------

--
-- Структура таблицы `answers_media`
--

CREATE TABLE `answers_media` (
  `answer_media_id` int NOT NULL,
  `answer_id` int NOT NULL,
  `media_type` enum('photo','document','video','audio','voice','etc') NOT NULL,
  `message_id` int NOT NULL,
  `file_id` text,
  `unique_file_id` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `assigned_groups`
--

CREATE TABLE `assigned_groups` (
  `assigned_group_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `group_id` int NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `groups`
--

CREATE TABLE `groups` (
  `group_id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'Название группы студентов'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `homeworks`
--

CREATE TABLE `homeworks` (
  `homework_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `text` text NOT NULL,
  `start` datetime DEFAULT NULL,
  `end` datetime NOT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Задания от преподавателей';

-- --------------------------------------------------------

--
-- Структура таблицы `homework_groups`
--

CREATE TABLE `homework_groups` (
  `homework_group_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `group_id` int NOT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sent_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Список выданных заданий для групп';

-- --------------------------------------------------------

--
-- Структура таблицы `homework_media`
--

CREATE TABLE `homework_media` (
  `homeworks_media_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `message_id` int NOT NULL,
  `file_id` text,
  `unique_file_id` text,
  `media_type` enum('photo','document','video','') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Файлы к заданию';

-- --------------------------------------------------------

--
-- Структура таблицы `students`
--

CREATE TABLE `students` (
  `student_id` int NOT NULL,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  `full_name` varchar(511) DEFAULT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `teachers`
--

CREATE TABLE `teachers` (
  `teacher_id` int NOT NULL,
  `user_id` int NOT NULL,
  `full_name` varchar(511) DEFAULT NULL,
  `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `telegram_users`
--

CREATE TABLE `telegram_users` (
  `user_id` int NOT NULL COMMENT 'ID в телеграмм',
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Таблица пользователей телеграмм';

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `admins`
--
ALTER TABLE `admins`
  ADD UNIQUE KEY `user_id_2` (`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Индексы таблицы `answers`
--
ALTER TABLE `answers`
  ADD PRIMARY KEY (`answer_id`),
  ADD KEY `student_id` (`student_id`),
  ADD KEY `homework_id` (`homework_id`,`student_id`);

--
-- Индексы таблицы `answers_media`
--
ALTER TABLE `answers_media`
  ADD PRIMARY KEY (`answer_media_id`),
  ADD KEY `answer_id` (`answer_id`);

--
-- Индексы таблицы `assigned_groups`
--
ALTER TABLE `assigned_groups`
  ADD PRIMARY KEY (`assigned_group_id`),
  ADD KEY `teacher_id` (`teacher_id`),
  ADD KEY `group_id` (`group_id`);

--
-- Индексы таблицы `groups`
--
ALTER TABLE `groups`
  ADD PRIMARY KEY (`group_id`),
  ADD KEY `name` (`name`);

--
-- Индексы таблицы `homeworks`
--
ALTER TABLE `homeworks`
  ADD PRIMARY KEY (`homework_id`),
  ADD KEY `teacher_id` (`teacher_id`);

--
-- Индексы таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  ADD PRIMARY KEY (`homework_group_id`),
  ADD KEY `group_id` (`group_id`),
  ADD KEY `homework_id` (`homework_id`,`group_id`);

--
-- Индексы таблицы `homework_media`
--
ALTER TABLE `homework_media`
  ADD PRIMARY KEY (`homeworks_media_id`),
  ADD KEY `homework_id` (`homework_id`);

--
-- Индексы таблицы `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`student_id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `group_id` (`group_id`),
  ADD KEY `user_id_2` (`user_id`);

--
-- Индексы таблицы `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`teacher_id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `user_id_2` (`user_id`);

--
-- Индексы таблицы `telegram_users`
--
ALTER TABLE `telegram_users`
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD KEY `user_id_2` (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `answers`
--
ALTER TABLE `answers`
  MODIFY `answer_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `answers_media`
--
ALTER TABLE `answers_media`
  MODIFY `answer_media_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `assigned_groups`
--
ALTER TABLE `assigned_groups`
  MODIFY `assigned_group_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `groups`
--
ALTER TABLE `groups`
  MODIFY `group_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `homeworks`
--
ALTER TABLE `homeworks`
  MODIFY `homework_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  MODIFY `homework_group_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `homework_media`
--
ALTER TABLE `homework_media`
  MODIFY `homeworks_media_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `students`
--
ALTER TABLE `students`
  MODIFY `student_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `teachers`
--
ALTER TABLE `teachers`
  MODIFY `teacher_id` int NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `admins`
--
ALTER TABLE `admins`
  ADD CONSTRAINT `admins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `answers`
--
ALTER TABLE `answers`
  ADD CONSTRAINT `answers_ibfk_1` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`homework_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `answers_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `answers_media`
--
ALTER TABLE `answers_media`
  ADD CONSTRAINT `answers_media_ibfk_1` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`answer_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `assigned_groups`
--
ALTER TABLE `assigned_groups`
  ADD CONSTRAINT `assigned_groups_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `assigned_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `homeworks`
--
ALTER TABLE `homeworks`
  ADD CONSTRAINT `homeworks_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  ADD CONSTRAINT `homework_groups_ibfk_1` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`homework_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `homework_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `homework_media`
--
ALTER TABLE `homework_media`
  ADD CONSTRAINT `homework_media_ibfk_1` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`homework_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `students_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

--
-- Ограничения внешнего ключа таблицы `teachers`
--
ALTER TABLE `teachers`
  ADD CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
