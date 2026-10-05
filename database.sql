-- College Digital Library Management Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin
-- Database Name: college_library_db

CREATE DATABASE IF NOT EXISTS `college_library_db`;
USE `college_library_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `name` VARCHAR(100) DEFAULT 'Administrator',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

-- Table structure for books
CREATE TABLE IF NOT EXISTS `books` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `author` VARCHAR(100) NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `description` TEXT,
    `filename` VARCHAR(255) NOT NULL,
    `upload_date` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for downloads
CREATE TABLE IF NOT EXISTS `downloads` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `download_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
);

-- Seed Default Admin Account (Username: admin | Password: admin123)
-- Password hash generated using Werkzeug pbkdf2:sha256
INSERT INTO `admins` (`username`, `password_hash`, `name`) VALUES
('admin', 'scrypt:32768:8:1$uJ8m4P7n4m1X$f4e1f74fa124ad9020fb0037a344d56d11f81e88f57adbd8e20252b4bc66ef6c11db89aa59fec3aeb1a6ea90c41031c51dbba5a0d3bd2f3fcd4ff90ffcf46e55', 'System Administrator')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed Sample Digital Books
INSERT INTO `books` (`title`, `author`, `category`, `description`, `filename`) VALUES
('Python Programming Fundamentals', 'Guido van Rossum', 'Programming', 'Comprehensive guide to Python syntax, data structures, and object-oriented concepts.', 'sample_python_guide.pdf'),
('Database Management Systems & SQL', 'Raghu Ramakrishnan', 'Database', 'In-depth introduction to relational databases, SQL queries, normalization, and indexing.', 'sample_dbms_guide.pdf'),
('Modern Web Development with Flask & Bootstrap', 'Miguel Grinberg', 'Web Development', 'Practical reference for building modern full-stack web applications using Flask and Bootstrap 5.', 'sample_web_dev_guide.pdf'),
('Data Structures and Algorithms in Python', 'Michael T. Goodrich', 'Computer Science', 'Core computer science algorithms, complexity analysis, trees, graphs, and sorting.', 'sample_dsa_guide.pdf');
