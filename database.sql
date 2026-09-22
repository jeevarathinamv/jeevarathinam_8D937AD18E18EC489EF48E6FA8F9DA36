-- Student Course & Certification Tracker
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_course_tracker`;
USE `student_course_tracker`;

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

-- Table structure for courses
CREATE TABLE IF NOT EXISTS `courses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `course_name` VARCHAR(150) NOT NULL,
    `course_provider` VARCHAR(100) NOT NULL,
    `course_category` VARCHAR(100) NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE DEFAULT NULL,
    `course_status` VARCHAR(20) NOT NULL DEFAULT 'Ongoing', -- Ongoing, Completed
    `course_link` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for certifications
CREATE TABLE IF NOT EXISTS `certifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `certificate_name` VARCHAR(150) NOT NULL,
    `course_name` VARCHAR(150) NOT NULL,
    `issuing_organization` VARCHAR(100) NOT NULL,
    `issue_date` DATE NOT NULL,
    `certificate_id` VARCHAR(100) DEFAULT NULL,
    `certificate_link` VARCHAR(255) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sample initial admin account (username: admin, password: password_hash for admin123 or managed in app code)
-- Will be seeded automatically if table is empty in app startup or sql script.
