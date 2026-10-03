-- ============================================================
-- College Entrepreneurship Idea Submission Portal
-- Database Schema & Setup Guide for MySQL / XAMPP phpMyAdmin
-- ============================================================
-- Instructions:
-- 1. Open XAMPP Control Panel and start Apache & MySQL modules.
-- 2. Open http://localhost/phpmyadmin in your browser.
-- 3. Click on "Import" tab and select this database.sql file.
-- 4. Click "Go" to execute and build the database and tables.
-- ============================================================

CREATE DATABASE IF NOT EXISTS `college_entrepreneurship_portal`;
USE `college_entrepreneurship_portal`;

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
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

-- Table structure for ideas
CREATE TABLE IF NOT EXISTS `ideas` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `idea_id` VARCHAR(50) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `problem_statement` TEXT NOT NULL,
    `proposed_solution` TEXT NOT NULL,
    `target_customers` TEXT NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `required_resources` TEXT NOT NULL,
    `estimated_budget` VARCHAR(100) NOT NULL,
    `expected_benefits` TEXT NOT NULL,
    `submission_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Options: Pending, Under Review, Approved, Rejected, Selected
    `admin_remarks` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for evaluations
CREATE TABLE IF NOT EXISTS `evaluations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `idea_id` INT UNIQUE NOT NULL,
    `innovation_score` INT NOT NULL DEFAULT 0,
    `feasibility_score` INT NOT NULL DEFAULT 0,
    `market_potential_score` INT NOT NULL DEFAULT 0,
    `social_impact_score` INT NOT NULL DEFAULT 0,
    `total_score` INT NOT NULL DEFAULT 0,
    `overall_remarks` TEXT,
    `evaluated_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`idea_id`) REFERENCES `ideas`(`id`) ON DELETE CASCADE
);

-- Seed default Admin account (Username: admin, Password: admin123)
-- Note: Werkzeug generated hash for 'admin123'
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$yGkFm1gT3341y7dJ$06ba75d50242a98fbdbe1cd851dd812bd26fa48e9c60eeb69bd3e573ef841cfd1eb96d44efbe2aefbf61833eec1438a25c61a5bce9be5c4a5c6ee16035d888e2')
ON DUPLICATE KEY UPDATE `username`=`username`;
