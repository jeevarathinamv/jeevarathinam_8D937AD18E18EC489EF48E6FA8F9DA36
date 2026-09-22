-- Smart College Student Help Desk System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `smart_college_helpdesk`;
USE `smart_college_helpdesk`;

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

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for help_requests
CREATE TABLE IF NOT EXISTS `help_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `category` VARCHAR(50) NOT NULL, -- Academic, Fees, Exam, Lab, Other
    `subject` VARCHAR(150) NOT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Resolved
    `admin_reply` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Default Admin Account (Username: admin, Password: pbkdf2 default for 'admin123')
-- Note: Admin account is also automatically auto-created by Flask app on initial run if not existing.
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$K7zE6Lz20O3J2vY5$f3521b2d4999d3e5e4d29f8f4803b984c17df3029a1b18dcdbf5bdc4e53bfa598cb6b4ec2b810d7a04dd3027ef4fb4aa5f17d3d63c5a6ad122d699564f331668')
ON DUPLICATE KEY UPDATE `username`=`username`;
