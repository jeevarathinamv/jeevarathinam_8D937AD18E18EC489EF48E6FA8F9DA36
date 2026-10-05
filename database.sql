-- College Canteen Feedback & Complaint System
-- Database Schema for MySQL / XAMPP phpMyAdmin

-- Setup Instructions for XAMPP / phpMyAdmin:
-- 1. Open XAMPP Control Panel and start Apache and MySQL services.
-- 2. Open browser and go to http://localhost/phpmyadmin/
-- 3. Click on 'Import' tab and upload this 'database.sql' file OR create database `canteen_feedback_db` and execute SQL queries below.
-- 4. Open VS Code, open project folder, install dependencies: `pip install -r requirements.txt`
-- 5. Run application: `python app.py`
-- 6. Access website at http://127.0.0.1:5000/

CREATE DATABASE IF NOT EXISTS `canteen_feedback_db`;
USE `canteen_feedback_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL DEFAULT 'Canteen Admin',
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

-- Table structure for feedback
CREATE TABLE IF NOT EXISTS `feedback` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `food_quality_rating` INT NOT NULL DEFAULT 5,
    `taste_rating` INT NOT NULL DEFAULT 5,
    `cleanliness_rating` INT NOT NULL DEFAULT 5,
    `service_rating` INT NOT NULL DEFAULT 5,
    `overall_rating` INT NOT NULL DEFAULT 5,
    `message` TEXT NOT NULL,
    `feedback_date` DATE NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for complaints
CREATE TABLE IF NOT EXISTS `complaints` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `complaint_id` VARCHAR(30) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `complaint_type` VARCHAR(50) NOT NULL,
    `description` TEXT NOT NULL,
    `complaint_date` DATE NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Pending', -- Pending, In Progress, Resolved, Rejected
    `admin_remarks` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Seed default admin account (Username: admin, Password: admin123)
-- Password hash generated using werkzeug pbkdf2:sha256
INSERT INTO `admins` (`username`, `password_hash`, `full_name`)
VALUES ('admin', 'scrypt:32768:8:1$u7xK3lG4H0vP8Xz1$30084f7b23114a840e60fa770cbfca96a5818fa860f4eebca8e469503ed7c82e705b0c7fa8732aef5c5f8507ba5ed2c263c9e6bb076615b801509a27e779cbf5', 'Main Canteen Administrator')
ON DUPLICATE KEY UPDATE `username`=`username`;
