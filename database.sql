-- College Library Book Issue & Return System
-- Database Schema and Initial Seed Data for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `college_library_db`;
USE `college_library_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table structure for books
CREATE TABLE IF NOT EXISTS `books` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `book_name` VARCHAR(150) NOT NULL,
    `author_name` VARCHAR(100) NOT NULL,
    `isbn` VARCHAR(50) UNIQUE NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `total_copies` INT NOT NULL DEFAULT 1,
    `available_copies` INT NOT NULL DEFAULT 1
);

-- Table structure for book_issues
CREATE TABLE IF NOT EXISTS `book_issues` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `issue_date` DATE NOT NULL,
    `due_date` DATE NOT NULL,
    `return_date` DATE NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Issued',
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
);

-- Seed Default Admin Credentials (Username: admin, Password: admin123)
INSERT INTO `admins` (`username`, `password`)
SELECT 'admin', 'scrypt:32768:8:1$BjlSY36PFUUVmm2I$3a67d9ca2d8511948e8d0851724868b912351328865b6916078be86de33f3fbc5f0ea896e9d498141bedadbf07a412a7d98664028a27dde5eafcd1e06dea601f'
WHERE NOT EXISTS (SELECT 1 FROM `admins` WHERE `username` = 'admin');

-- Seed Initial Books
INSERT INTO `books` (`book_name`, `author_name`, `isbn`, `category`, `total_copies`, `available_copies`) VALUES
('Python Programming: An Introduction', 'John Zelle', '978-1590282410', 'Programming', 5, 5),
('Database System Concepts', 'Abraham Silberschatz', '978-0078022159', 'Database', 4, 4),
('Learning Web Design', 'Jennifer Robbins', '978-1491960202', 'Web Development', 6, 6),
('Introduction to Algorithms', 'Thomas H. Cormen', '978-0262033848', 'Computer Science', 3, 3),
('Principles of Software Engineering', 'Ian Sommerville', '978-0133943030', 'Management', 4, 4),
('Clean Code: A Handbook of Agile Software Craftsmanship', 'Robert C. Martin', '978-0132350884', 'General', 5, 5),
('Artificial Intelligence: A Modern Approach', 'Stuart Russell', '978-0134610993', 'Other', 2, 2);
