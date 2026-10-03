-- Student Career Goal & Progress Tracker
-- Database Schema for MySQL / XAMPP phpMyAdmin
-- Project: MCA Student Project
--
-- INSTRUCTIONS FOR XAMPP / phpMyAdmin:
-- 1. Open XAMPP Control Panel and start Apache and MySQL.
-- 2. Open http://localhost/phpmyadmin in your web browser.
-- 3. Click on "Import" tab.
-- 4. Choose this `database.sql` file and click "Import".
-- 5. The database `student_career_tracker_db` will be created automatically.

CREATE DATABASE IF NOT EXISTS `student_career_tracker_db`;
USE `student_career_tracker_db`;

-- Table: admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: career_profiles
CREATE TABLE IF NOT EXISTS `career_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL UNIQUE,
    `career_objective` TEXT,
    `target_job_role` VARCHAR(100),
    `target_industry` VARCHAR(100),
    `skills` TEXT,
    `preferred_career_field` VARCHAR(100),
    `short_term_goal` TEXT,
    `long_term_goal` TEXT,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table: career_goals
CREATE TABLE IF NOT EXISTS `career_goals` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `description` TEXT,
    `start_date` DATE NOT NULL,
    `target_date` DATE NOT NULL,
    `priority` VARCHAR(20) NOT NULL DEFAULT 'Medium', -- High, Medium, Low
    `progress_percentage` INT NOT NULL DEFAULT 0,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Not Started', -- Not Started, In Progress, Completed, Overdue
    `notes` TEXT,
    `last_updated` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table: skills
CREATE TABLE IF NOT EXISTS `skills` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `skill_name` VARCHAR(100) NOT NULL,
    `skill_category` VARCHAR(50) NOT NULL,
    `skill_level` VARCHAR(20) NOT NULL DEFAULT 'Beginner', -- Beginner, Intermediate, Advanced
    `target_level` VARCHAR(20) NOT NULL DEFAULT 'Intermediate', -- Beginner, Intermediate, Advanced
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table: certifications
CREATE TABLE IF NOT EXISTS `certifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `name` VARCHAR(150) NOT NULL,
    `issuing_organization` VARCHAR(150) NOT NULL,
    `issue_date` DATE,
    `expiry_date` DATE,
    `certificate_id` VARCHAR(100),
    `certificate_link` VARCHAR(255),
    `status` VARCHAR(20) NOT NULL DEFAULT 'Active', -- Active, Expired, In Progress
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table: milestones
CREATE TABLE IF NOT EXISTS `milestones` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `milestone_type` VARCHAR(50) NOT NULL, -- Completed Course, Completed Certification, Finished Project, Internship, Placement Preparation, Interview Preparation
    `date_achieved` DATE NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Seed Initial Default Admin Credentials
-- Username: admin
-- Password: admin123 (hashed using werkzeug scrypt/pbkdf2)
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$K1M70L2b5F1n8jO7$c6b8c800889270659635fdb173b22ed70be8168233bb970ca8c53a693c06e12e')
ON DUPLICATE KEY UPDATE `id`=`id`;
