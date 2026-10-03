-- ==============================================================================
-- Student Workshop Registration System - Database Schema
-- MCA Academic Project
-- Target Database: MySQL (XAMPP phpMyAdmin) / Database Name: student_workshop_system
--
-- INSTRUCTIONS FOR XAMPP & PHPMYADMIN SETUP:
-- 1. Open XAMPP Control Panel and start Apache and MySQL services.
-- 2. Open browser and go to http://localhost/phpmyadmin/
-- 3. Click 'Import' tab, choose this 'database.sql' file, and click 'Go'.
-- 4. Alternatively, create database 'student_workshop_system' manually and import.
--
-- INSTRUCTIONS FOR PYTHON PACKAGE INSTALLATION:
-- Run: pip install flask flask-sqlalchemy pymysql
--
-- HOW TO RUN THE PROJECT IN VS CODE:
-- 1. Open project directory in VS Code.
-- 2. Run: python app.py  (or USE_SQLITE=1 python app.py if using SQLite)
-- 3. Open http://127.0.0.1:5000 in your browser.
--
-- DEFAULT ADMIN CREDENTIALS:
-- Username: admin
-- Password: admin123
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `student_workshop_system`;
USE `student_workshop_system`;

-- Table 1: students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `phone_number` VARCHAR(20) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: workshops
CREATE TABLE IF NOT EXISTS `workshops` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `category` VARCHAR(100) NOT NULL,
    `trainer_name` VARCHAR(100) NOT NULL,
    `date` DATE NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `venue` VARCHAR(150) NOT NULL,
    `total_seats` INT NOT NULL DEFAULT 0,
    `registration_deadline` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Upcoming',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: registrations
CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `registration_id` VARCHAR(50) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `workshop_id` INT NOT NULL,
    `registration_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Registered',
    UNIQUE KEY `unique_student_workshop` (`student_id`, `workshop_id`),
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workshop_id`) REFERENCES `workshops`(`id`) ON DELETE CASCADE
);

-- Table 5: attendance
CREATE TABLE IF NOT EXISTS `attendance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `registration_id` INT UNIQUE NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Absent',
    `marked_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`registration_id`) REFERENCES `registrations`(`id`) ON DELETE CASCADE
);

-- Seed Default Admin Account (Username: admin, Password: admin123)
INSERT INTO `admins` (`username`, `password_hash`, `name`)
VALUES ('admin', 'scrypt:32768:8:1$uH34EGHW$a91fcd5e5233c706509fca94017fbb82d2bbad9d2f6f571b05bcbd0644c9b980974edc55e9ea273f081498b6ad851f5e27ecbbdb6fb44e5d6d84f8efef6e4dcb', 'System Administrator')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed Sample Workshops
INSERT INTO `workshops` (`title`, `description`, `category`, `trainer_name`, `date`, `start_time`, `end_time`, `venue`, `total_seats`, `registration_deadline`, `status`) VALUES
('Full Stack Web Development with Flask & React', 'Learn full stack web application development using Python Flask and React JS with hands-on project implementation.', 'Web Development', 'Dr. Aris Thorne', '2025-04-15', '09:30:00', '12:30:00', 'Seminar Hall A', 40, '2025-04-14', 'Upcoming'),
('Data Science & Machine Learning Fundamentals', 'An introductory workshop covering data analysis, Python Pandas, Scikit-Learn, and building predictive models.', 'Data Science', 'Prof. Sarah Jenkins', '2025-04-20', '10:00:00', '13:00:00', 'Computer Lab 3', 30, '2025-04-19', 'Upcoming'),
('Ethical Hacking & Cyber Security Essentials', 'Understand network security fundamentals, penetration testing concepts, and defensive cyber security strategies.', 'Cyber Security', 'Alex Mercer', '2025-04-25', '14:00:00', '17:00:00', 'Auditorium', 50, '2025-04-24', 'Upcoming'),
('Cloud Computing with AWS Fundamentals', 'Introduction to Amazon Web Services, cloud architecture, EC2 instances, S3 storage, and deployment models.', 'Cloud Computing', 'Vikram Malhotra', '2025-05-02', '10:00:00', '12:30:00', 'Seminar Hall B', 35, '2025-05-01', 'Upcoming'),
('Soft Skills & Leadership for IT Professionals', 'Interactive session focusing on communication skills, resume building, interview techniques, and team leadership.', 'Soft Skills', 'Clara Vance', '2025-05-10', '11:00:00', '13:00:00', 'Conference Room 1', 60, '2025-05-09', 'Upcoming');
