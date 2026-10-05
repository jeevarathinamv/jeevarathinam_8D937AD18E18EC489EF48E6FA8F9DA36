-- Classroom Maintenance Complaint Tracker
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `classroom_maintenance_db`;
USE `classroom_maintenance_db`;

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

-- Table structure for complaints
CREATE TABLE IF NOT EXISTS `complaints` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `complaint_id` VARCHAR(20) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `classroom_number` VARCHAR(50) NOT NULL,
    `complaint_type` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `complaint_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Resolved, Rejected
    `admin_remarks` TEXT,
    `resolved_date` DATE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Note: Default admin account will be created automatically on app startup.
-- Default Credentials: Username: admin | Password: admin123
