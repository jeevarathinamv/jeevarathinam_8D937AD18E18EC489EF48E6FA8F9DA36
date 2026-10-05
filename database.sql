-- Library Book Fine Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `library_fine_db`;
USE `library_fine_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
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
    `book_name` VARCHAR(200) NOT NULL,
    `author_name` VARCHAR(150) NOT NULL,
    `book_code` VARCHAR(50) UNIQUE NOT NULL,
    `category` VARCHAR(100) NOT NULL,
    `available_copies` INT NOT NULL DEFAULT 1,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for book issues
CREATE TABLE IF NOT EXISTS `book_issues` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `issue_date` DATE NOT NULL,
    `due_date` DATE NOT NULL,
    `return_date` DATE NULL,
    `status` VARCHAR(20) DEFAULT 'Issued', -- Issued, Returned, Overdue
    `late_days` INT DEFAULT 0,
    `fine_amount` DECIMAL(10,2) DEFAULT 0.00,
    `fine_status` VARCHAR(20) DEFAULT 'No Fine', -- No Fine, Pending, Paid
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
);

-- Seed Default Admin Credentials
-- Username: admin
-- Password: admin123 (scrypt hashed password)
INSERT INTO `admins` (`username`, `password_hash`, `name`) VALUES
('admin', 'scrypt:32768:8:1$vO5vBfO5gS8J62fT$24ef5476a0d4218a4a3ed775e54d588ceba658b105d15cb1fbdcb2758efc3ad18ef49bb40b39ad2827aef934c919d38116b9b348d3db841fefee84d0ecfb31ed', 'Library Admin')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Initial Sample Books
INSERT INTO `books` (`book_name`, `author_name`, `book_code`, `category`, `available_copies`) VALUES
('Python Crash Course', 'Eric Matthes', 'BK-CS-001', 'Computer Science', 5),
('Clean Code', 'Robert C. Martin', 'BK-CS-002', 'Computer Science', 3),
('Introduction to Algorithms', 'Thomas H. Cormen', 'BK-CS-003', 'Computer Science', 4),
('Database System Concepts', 'Abraham Silberschatz', 'BK-CS-004', 'Information Technology', 6),
('Operating System Concepts', 'Abraham Silberschatz', 'BK-CS-005', 'Computer Science', 2)
ON DUPLICATE KEY UPDATE `id`=`id`;
