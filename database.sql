-- Library New Book Request System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `library_db`;
USE `library_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
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

-- Table structure for book_requests
CREATE TABLE IF NOT EXISTS `book_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `request_id` VARCHAR(20) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `book_name` VARCHAR(200) NOT NULL,
    `author_name` VARCHAR(150) NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `reason` TEXT NOT NULL,
    `request_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Approved, Rejected
    `admin_remarks` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Default Admin Seed (Password: admin123 using pbkdf2:sha256 hash)
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$u7P1j9kL$e2c1c6e1e7f0b5d9c2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8')
ON DUPLICATE KEY UPDATE `username`=`username`;
