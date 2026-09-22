-- Student Mock Interview Practice Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `mock_interview_db`;
USE `mock_interview_db`;

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for interview categories
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) UNIQUE NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for interview questions
CREATE TABLE IF NOT EXISTS `questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_id` INT NOT NULL,
    `question_text` TEXT NOT NULL,
    `sample_answer` TEXT NOT NULL,
    `keywords` TEXT NOT NULL, -- Comma-separated key concepts for scoring evaluation
    `max_marks` INT NOT NULL DEFAULT 10,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE
);

-- Table structure for interview attempts
CREATE TABLE IF NOT EXISTS `interview_attempts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `category_id` INT NOT NULL,
    `total_score` FLOAT NOT NULL DEFAULT 0,
    `max_possible_score` FLOAT NOT NULL DEFAULT 0,
    `percentage` FLOAT NOT NULL DEFAULT 0,
    `feedback` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE CASCADE
);

-- Table structure for individual question answers within an attempt
CREATE TABLE IF NOT EXISTS `interview_answers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `attempt_id` INT NOT NULL,
    `question_id` INT NOT NULL,
    `user_answer` TEXT,
    `score` FLOAT NOT NULL DEFAULT 0,
    `max_marks` INT NOT NULL DEFAULT 10,
    `feedback` TEXT,
    FOREIGN KEY (`attempt_id`) REFERENCES `interview_attempts`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON DELETE CASCADE
);

-- Insert Default Categories
INSERT INTO `categories` (`name`, `description`) VALUES
('Python', 'Core Python concepts, data structures, OOP, and standard library questions.'),
('Java', 'Java fundamentals, Object-Oriented Programming, collections, and exception handling.'),
('SQL', 'Relational database concepts, SQL queries, joins, indexing, and aggregations.'),
('HR', 'Behavioral, situational, soft skills, and HR interview questions.');

-- Insert Default Questions
INSERT INTO `questions` (`category_id`, `question_text`, `sample_answer`, `keywords`, `max_marks`) VALUES
-- Python Questions
(1, 'What is the difference between list and tuple in Python?', 'Lists are mutable while tuples are immutable. Lists use square brackets [] whereas tuples use parentheses ().', 'mutable, immutable, brackets, parentheses, tuple, list', 10),
(1, 'Explain PEP 8 and why it is important.', 'PEP 8 is Python\'s style guide. It provides guidelines and best practices on how to format Python code for readability and consistency.', 'style, guide, readability, formatting, guidelines, standard', 10),
(1, 'What are decorators in Python and how do they work?', 'A decorator is a design pattern in Python used to extend or modify the behavior of a function or method without altering its actual code structure.', 'function, modify, behavior, wrapper, pattern, extend', 10),

-- Java Questions
(2, 'What are the main principles of Object-Oriented Programming (OOP) in Java?', 'The four main OOP principles in Java are Encapsulation, Inheritance, Polymorphism, and Abstraction.', 'encapsulation, inheritance, polymorphism, abstraction, oop', 10),
(2, 'What is the difference between JDK, JRE, and JVM?', 'JVM executes bytecode, JRE provides libraries and runtime environment, and JDK is the development kit containing debugging tools and compiler.', 'jvm, jre, jdk, bytecode, runtime, compiler, development', 10),

-- SQL Questions
(3, 'What is the difference between INNER JOIN and LEFT JOIN in SQL?', 'INNER JOIN returns records that have matching values in both tables, while LEFT JOIN returns all records from the left table and matched records from the right table.', 'inner, left, join, matching, records, left table, right table', 10),
(3, 'What is a Primary Key and how does it differ from a Unique Key?', 'A Primary Key uniquely identifies a record and cannot contain NULL values, whereas a Unique Key prevents duplicate values but can accept one NULL value.', 'primary key, unique key, null, duplicate, unique, record', 10),

-- HR Questions
(4, 'Tell me about yourself and your professional goals.', 'I am a dedicated student passionate about technology and software development. My goal is to build a successful career by continuously learning and solving real-world problems.', 'passion, learning, goals, technology, development, dedicated, problem', 10),
(4, 'How do you handle pressure or tight deadlines?', 'I prioritize tasks, break down complex requirements into smaller milestones, maintain clear communication, and remain focused on delivery.', 'prioritize, focus, deadline, communication, milestone, pressure, task', 10);
