-- Student Portfolio Website Generator
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_portfolio`;
USE `student_portfolio`;

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

-- Table structure for profiles
CREATE TABLE IF NOT EXISTS `profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNIQUE NOT NULL,
    `profile_photo` VARCHAR(255) DEFAULT 'default_avatar.png',
    `about_me` TEXT,
    `career_objective` TEXT,
    `hobbies` TEXT,
    `phone` VARCHAR(20),
    `address` TEXT,
    `linkedin_url` VARCHAR(255),
    `github_url` VARCHAR(255),
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for education
CREATE TABLE IF NOT EXISTS `education` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `degree` VARCHAR(100) NOT NULL,
    `institution` VARCHAR(150) NOT NULL,
    `year_of_passing` VARCHAR(20) NOT NULL,
    `score` VARCHAR(50) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for skills
CREATE TABLE IF NOT EXISTS `skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `skill_name` VARCHAR(100) NOT NULL,
    `proficiency` VARCHAR(50) DEFAULT 'Intermediate',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for projects
CREATE TABLE IF NOT EXISTS `projects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `description` TEXT NOT NULL,
    `technologies_used` VARCHAR(255) NOT NULL,
    `project_link` VARCHAR(255),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for certifications
CREATE TABLE IF NOT EXISTS `certifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `certificate_title` VARCHAR(150) NOT NULL,
    `issuing_organization` VARCHAR(150) NOT NULL,
    `issue_date` VARCHAR(50),
    `certificate_link` VARCHAR(255),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Seed Default Admin User (username: admin, password: adminpassword)
-- Password hash generated using pbkdf2:sha256
INSERT INTO `admins` (`username`, `password_hash`)
SELECT 'admin', 'scrypt:32768:8:1$Kq1Z14c6Xm9c1vRk$d5b5eb00cf08bd165eb3d154ee4263539fb0426be048b64b18c64bbdd49e17db17c8008a0e882aef4a5e3df17f919d7d42cf7b0cefb0213aa672534571d7d079'
WHERE NOT EXISTS (SELECT 1 FROM `admins` WHERE `username` = 'admin');
