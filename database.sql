-- Internship Application & Follow-up Tracker
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `internship_tracker`;
USE `internship_tracker`;

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for internship applications
CREATE TABLE IF NOT EXISTS `internship_applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `company_name` VARCHAR(100) NOT NULL,
    `role` VARCHAR(100) NOT NULL,
    `location` VARCHAR(100) NOT NULL,
    `application_date` DATE NOT NULL,
    `application_link` VARCHAR(255) DEFAULT NULL,
    `status` VARCHAR(50) DEFAULT 'Applied', -- Status: Applied, Shortlisted, Interview Scheduled, Selected, Rejected
    `interview_date` DATE DEFAULT NULL,
    `notes` TEXT DEFAULT NULL,
    `admin_remarks` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for follow-ups
CREATE TABLE IF NOT EXISTS `followups` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `application_id` INT NOT NULL,
    `followup_date` DATE NOT NULL,
    `notes` TEXT NOT NULL,
    `updated_status` VARCHAR(50) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`application_id`) REFERENCES `internship_applications`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed initial admin user (username: admin, password: admin123)
-- Hash generated using werkzeug generate_password_hash('admin123')
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$C1W2v4fS7z3J9q$c7128527a29e4b7b3e0c034edffea0971239c4a8ee1f1f91fb342b4b4dd4f923a54d68800bb8db1e8a9391d16ec85c496be6ef4dd8a313d420f17e3f8ec47d3c')
ON DUPLICATE KEY UPDATE `id`=`id`;
