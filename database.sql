-- Student Freelance Project Management Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `freelance_db`;
USE `freelance_db`;

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

-- Table structure for student profiles
CREATE TABLE IF NOT EXISTS `student_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNIQUE NOT NULL,
    `photo` VARCHAR(255) DEFAULT 'default_profile.png',
    `skills` TEXT,
    `experience` TEXT,
    `bio` TEXT,
    `portfolio_link` VARCHAR(255),
    `contact_email` VARCHAR(120),
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for clients
CREATE TABLE IF NOT EXISTS `clients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20),
    `email` VARCHAR(120),
    `company_name` VARCHAR(100),
    `address` TEXT,
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for projects
CREATE TABLE IF NOT EXISTS `projects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `client_id` INT,
    `title` VARCHAR(150) NOT NULL,
    `client_name` VARCHAR(100) NOT NULL,
    `description` TEXT,
    `category` VARCHAR(50),
    `start_date` DATE,
    `deadline` DATE,
    `budget` DECIMAL(10, 2) DEFAULT 0.00,
    `status` VARCHAR(20) DEFAULT 'New', -- New, In Progress, On Hold, Completed, Cancelled
    `progress_percentage` INT DEFAULT 0,
    `progress_notes` TEXT,
    `last_updated_date` DATE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`client_id`) REFERENCES `clients`(`id`) ON DELETE SET NULL
);

-- Table structure for tasks
CREATE TABLE IF NOT EXISTS `tasks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `project_id` INT NOT NULL,
    `student_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `description` TEXT,
    `due_date` DATE,
    `priority` VARCHAR(20) DEFAULT 'Medium', -- High, Medium, Low
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Completed
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for payments
CREATE TABLE IF NOT EXISTS `payments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `project_id` INT NOT NULL,
    `student_id` INT NOT NULL,
    `client_name` VARCHAR(100) NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `payment_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Partially Paid, Paid
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Default Admin Credentials Insert (password: admin123)
-- Note: Admin login can also be handled with hardcoded fallback in app.py
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$2P91M9x6z...$...') ON DUPLICATE KEY UPDATE `username`=`username`;
