-- phpMyAdmin SQL Dump
-- version 5.2.1deb3
-- https://www.phpmyadmin.net/
--
-- Хост: localhost:3306
-- Время создания: Дек 11 2025 г., 16:58
-- Версия сервера: 8.0.44-0ubuntu0.24.04.2
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
CREATE DATABASE IF NOT EXISTS `bot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `bot`;

-- --------------------------------------------------------

--
-- Структура таблицы `admins`
--

CREATE TABLE `admins` (
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Администраторы';

--
-- ССЫЛКИ ТАБЛИЦЫ `admins`:
--   `user_id`
--       `telegram_users` -> `user_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `answers`
--

CREATE TABLE `answers` (
  `answer_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `student_id` int NOT NULL,
  `student_answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT 'Ответ студента',
  `status` enum('sent','reviewed','rejected','accepted') NOT NULL COMMENT 'Статусы проверки преподавателя',
  `grade` tinyint DEFAULT NULL COMMENT 'Оценка преподавателя',
  `teacher_comment` text,
  `sent_at` datetime NOT NULL COMMENT 'Время отправки ответа',
  `checked_at` datetime DEFAULT NULL COMMENT 'Время проверки ответа'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Ответы студентов на задания с оценкой преподователя';

--
-- ССЫЛКИ ТАБЛИЦЫ `answers`:
--   `homework_id`
--       `homeworks` -> `homework_id`
--   `student_id`
--       `students` -> `student_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `answer_files`
--

CREATE TABLE `answer_files` (
  `answer_file_id` int NOT NULL,
  `answer_id` int NOT NULL,
  `telegram_file_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Файлы к ответам';

--
-- ССЫЛКИ ТАБЛИЦЫ `answer_files`:
--   `answer_id`
--       `answers` -> `answer_id`
--   `telegram_file_id`
--       `telegram_files` -> `telegram_file_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `assigned_groups`
--

CREATE TABLE `assigned_groups` (
  `assigned_group_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `group_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Группы закрепленные за преподавателем';

--
-- ССЫЛКИ ТАБЛИЦЫ `assigned_groups`:
--   `teacher_id`
--       `teachers` -> `teacher_id`
--   `group_id`
--       `groups` -> `group_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `groups`
--

CREATE TABLE `groups` (
  `group_id` int NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'Название группы студентов'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- ССЫЛКИ ТАБЛИЦЫ `groups`:
--

-- --------------------------------------------------------

--
-- Структура таблицы `homeworks`
--

CREATE TABLE `homeworks` (
  `homework_id` int NOT NULL,
  `teacher_id` int NOT NULL,
  `title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `text` text NOT NULL,
  `start_at` datetime DEFAULT NULL,
  `end_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Задания от преподавателей';

--
-- ССЫЛКИ ТАБЛИЦЫ `homeworks`:
--   `teacher_id`
--       `teachers` -> `teacher_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `homework_files`
--

CREATE TABLE `homework_files` (
  `homeworks_file_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `telegram_file_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Файлы к заданию';

--
-- ССЫЛКИ ТАБЛИЦЫ `homework_files`:
--   `homework_id`
--       `homeworks` -> `homework_id`
--   `homeworks_file_id`
--       `telegram_files` -> `telegram_file_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `homework_groups`
--

CREATE TABLE `homework_groups` (
  `homework_group_id` int NOT NULL,
  `homework_id` int NOT NULL,
  `group_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sent_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Список выданных заданий для групп';

--
-- ССЫЛКИ ТАБЛИЦЫ `homework_groups`:
--   `homework_id`
--       `homeworks` -> `homework_id`
--   `group_id`
--       `groups` -> `group_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `students`
--

CREATE TABLE `students` (
  `student_id` int NOT NULL,
  `user_id` int NOT NULL,
  `group_id` int DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- ССЫЛКИ ТАБЛИЦЫ `students`:
--   `user_id`
--       `telegram_users` -> `user_id`
--   `group_id`
--       `groups` -> `group_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `teachers`
--

CREATE TABLE `teachers` (
  `teacher_id` int NOT NULL,
  `user_id` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- ССЫЛКИ ТАБЛИЦЫ `teachers`:
--   `user_id`
--       `telegram_users` -> `user_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `telegram_files`
--

CREATE TABLE `telegram_files` (
  `telegram_file_id` int NOT NULL,
  `file_id` text NOT NULL COMMENT 'Текущий file_id для отправки файла (может меняться!)',
  `unique_file_id` text NOT NULL COMMENT 'Стабильный уникальный идентификатор файла',
  `file_type` text NOT NULL COMMENT 'Тип файла',
  `owner_user_id` int NOT NULL COMMENT 'От кого был переслан файл',
  `caption` text COMMENT 'Описание для файла',
  `mime_type` text COMMENT 'Тип содержимого',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Файлы из телеграмм';

--
-- ССЫЛКИ ТАБЛИЦЫ `telegram_files`:
--   `owner_user_id`
--       `telegram_users` -> `user_id`
--

-- --------------------------------------------------------

--
-- Структура таблицы `telegram_users`
--

CREATE TABLE `telegram_users` (
  `user_id` int NOT NULL COMMENT 'ID в телеграмм',
  `username` varchar(63) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Короткое имя в телеграмм',
  `full_name` varchar(127) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Отображаемое имя в телеграмм',
  `real_full_name` varchar(127) DEFAULT NULL COMMENT 'Полное реальное имя человека'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Таблица пользователей телеграмм';

--
-- ССЫЛКИ ТАБЛИЦЫ `telegram_users`:
--

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
-- Индексы таблицы `answer_files`
--
ALTER TABLE `answer_files`
  ADD PRIMARY KEY (`answer_file_id`),
  ADD KEY `answer_id` (`answer_id`),
  ADD KEY `telegram_file_id` (`telegram_file_id`);

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
-- Индексы таблицы `homework_files`
--
ALTER TABLE `homework_files`
  ADD PRIMARY KEY (`homeworks_file_id`),
  ADD KEY `homework_id` (`homework_id`);

--
-- Индексы таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  ADD PRIMARY KEY (`homework_group_id`),
  ADD KEY `group_id` (`group_id`),
  ADD KEY `homework_id` (`homework_id`,`group_id`);

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
-- Индексы таблицы `telegram_files`
--
ALTER TABLE `telegram_files`
  ADD PRIMARY KEY (`telegram_file_id`),
  ADD KEY `owner_user_id` (`owner_user_id`);

--
-- Индексы таблицы `telegram_users`
--
ALTER TABLE `telegram_users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `answers`
--
ALTER TABLE `answers`
  MODIFY `answer_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `answer_files`
--
ALTER TABLE `answer_files`
  MODIFY `answer_file_id` int NOT NULL AUTO_INCREMENT;

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
-- AUTO_INCREMENT для таблицы `homework_files`
--
ALTER TABLE `homework_files`
  MODIFY `homeworks_file_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  MODIFY `homework_group_id` int NOT NULL AUTO_INCREMENT;

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
-- AUTO_INCREMENT для таблицы `telegram_files`
--
ALTER TABLE `telegram_files`
  MODIFY `telegram_file_id` int NOT NULL AUTO_INCREMENT;

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
-- Ограничения внешнего ключа таблицы `answer_files`
--
ALTER TABLE `answer_files`
  ADD CONSTRAINT `answer_files_ibfk_1` FOREIGN KEY (`answer_id`) REFERENCES `answers` (`answer_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `answer_files_ibfk_2` FOREIGN KEY (`telegram_file_id`) REFERENCES `telegram_files` (`telegram_file_id`) ON DELETE CASCADE ON UPDATE CASCADE;

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
-- Ограничения внешнего ключа таблицы `homework_files`
--
ALTER TABLE `homework_files`
  ADD CONSTRAINT `homework_files_ibfk_1` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`homework_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `homework_files_ibfk_2` FOREIGN KEY (`homeworks_file_id`) REFERENCES `telegram_files` (`telegram_file_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `homework_groups`
--
ALTER TABLE `homework_groups`
  ADD CONSTRAINT `homework_groups_ibfk_1` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`homework_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `homework_groups_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `students`
--
ALTER TABLE `students`
  ADD CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `students_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE SET NULL ON UPDATE SET NULL;

--
-- Ограничения внешнего ключа таблицы `teachers`
--
ALTER TABLE `teachers`
  ADD CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ограничения внешнего ключа таблицы `telegram_files`
--
ALTER TABLE `telegram_files`
  ADD CONSTRAINT `telegram_files_ibfk_1` FOREIGN KEY (`owner_user_id`) REFERENCES `telegram_users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
