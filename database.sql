-- College Student Grievance Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `college_grievance`;
USE `college_grievance`;

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
    `email` VARCHAR(120) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for grievances
CREATE TABLE IF NOT EXISTS `grievances` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `subject` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Resolved, Rejected
    `admin_reply` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Seed default admin account (username: admin, password: admin123)
-- Password hash generated using Werkzeug security
INSERT INTO `admins` (`username`, `password_hash`, `email`, `name`) VALUES
('admin', 'scrypt:32768:8:1$7uKzV19616h2U43g$dcd413b5ef24805bb528a49c9eb11c0ed38d0eef7fcf64188fa6c5ecf05dfa02d8bf4e8c1c5cd700d9fcd18e11b4ba251ee2b144fa5eece19c6f2df3a9edecfa', 'admin@college.edu', 'System Administrator')
ON DUPLICATE KEY UPDATE `username`=`username`;
