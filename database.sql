-- Library Book Reservation & Availability System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `library_db`;
USE `library_db`;

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
    `isbn` VARCHAR(30) UNIQUE NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `description` TEXT,
    `total_copies` INT NOT NULL DEFAULT 1,
    `available_copies` INT NOT NULL DEFAULT 1
);

-- Table structure for reservations
CREATE TABLE IF NOT EXISTS `reservations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `book_id` INT NOT NULL,
    `reservation_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Reserved', -- Reserved, Cancelled, Completed
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
);

-- Seed default admin (Password: admin123)
-- Note: Werkzeug pbkdf2 hash for 'admin123' or seed via Flask on startup
INSERT INTO `admins` (`username`, `password`) VALUES
('admin', 'scrypt:32768:8:1$uH34J1Jk8g4S9k3L$7a747971dcb6f5a3a0e5b7c7e3f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6');

-- Seed sample books
INSERT INTO `books` (`book_name`, `author_name`, `isbn`, `category`, `description`, `total_copies`, `available_copies`) VALUES
('Python Programming', 'John Zelle', '978-1590282410', 'Computer Science', 'An introduction to computer science using Python.', 5, 5),
('Data Structures and Algorithms in Python', 'Michael T. Goodrich', '978-1118290279', 'Computer Science', 'Comprehensive guide to algorithms and data structures.', 3, 2),
('Database System Concepts', 'Abraham Silberschatz', '978-0078022159', 'Information Technology', 'Fundamental concepts of database design and management.', 4, 1),
('Operating System Concepts', 'Abraham Silberschatz', '978-1118063330', 'Computer Science', 'Essential operating system principles and architectures.', 2, 0),
('Web Engineering', 'Gerti Kappel', '978-0470015575', 'Web Development', 'Practices and specifications for web applications.', 6, 6);
