-- Alumni Mentorship & Career Guidance Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `alumni_mentorship`;
USE `alumni_mentorship`;

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

-- Table structure for alumni
CREATE TABLE IF NOT EXISTS `alumni` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `graduation_year` INT NOT NULL,
    `job_role` VARCHAR(100) NOT NULL,
    `company` VARCHAR(100) NOT NULL,
    `experience` VARCHAR(50) NOT NULL DEFAULT '2+ Years',
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for mentorship_requests
CREATE TABLE IF NOT EXISTS `mentorship_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `alumni_id` INT NOT NULL,
    `question` TEXT NOT NULL,
    `response` TEXT DEFAULT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Accepted, Rejected
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`alumni_id`) REFERENCES `alumni`(`id`) ON DELETE CASCADE
);

-- Table structure for career_guidance
CREATE TABLE IF NOT EXISTS `career_guidance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `alumni_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `category` VARCHAR(50) NOT NULL, -- Career Advice, Interview Tips, Resume Tips, Skill Suggestions
    `content` TEXT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`alumni_id`) REFERENCES `alumni`(`id`) ON DELETE CASCADE
);

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default Admin Account (Username: admin, Password: pbkdf2 hash for admin123)
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'pbkdf2:sha256:600000$8zW3x7yL$d6f3b06168340d8906c624d6bb0a221f73b8dfa32e18ebf5c7fa3b754877ad45')
ON DUPLICATE KEY UPDATE `id`=`id`;
