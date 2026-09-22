-- Student Attendance & Shortage Alert System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_attendance`;
USE `student_attendance`;

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
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for attendance
CREATE TABLE IF NOT EXISTS `attendance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `subject` VARCHAR(100) NOT NULL,
    `date` DATE NOT NULL,
    `status` VARCHAR(20) NOT NULL, -- 'Present' or 'Absent'
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Sample default admin user (Username: admin, Password: pbkdf2 hash for admin123)
INSERT INTO `admins` (`username`, `email`, `password_hash`) VALUES
('admin', 'admin@college.edu', 'scrypt:32768:8:1$vO5U8k81458O2Gk2$b0e8efc16640c6c74fb37bf1e992982d61a2ddfa00ffddba48ef4e138a0c2ed178a9cba2598be5e0e7a17737d2f9d6837eb5f0883d6a455a1532f913d87db10f')
ON DUPLICATE KEY UPDATE `username`=`username`;
