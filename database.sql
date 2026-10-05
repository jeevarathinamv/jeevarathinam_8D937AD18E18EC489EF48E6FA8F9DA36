-- College Academic Calendar Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `academic_calendar_db`;
USE `academic_calendar_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for academic_events
CREATE TABLE IF NOT EXISTS `academic_events` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `event_title` VARCHAR(150) NOT NULL,
    `event_type` VARCHAR(50) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `semester` VARCHAR(20) NOT NULL,
    `start_date` DATE NOT NULL,
    `end_date` DATE NOT NULL,
    `venue` VARCHAR(150) NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed default admin account (username: admin, password: pbkdf2:sha256:600000$hashed or admin123)
-- Note: app.py handles automatic admin creation with secure hashing if not present.
INSERT INTO `admins` (`username`, `password`) VALUES
('admin', 'scrypt:32768:8:1$uH3y4dY6gXf5J9kZ$0b115456456722d71d3e8e2c0e3a6f3b0e115456456722d71d3e8e2c0e3a6f3b');

-- Seed sample academic events
INSERT INTO `academic_events` (`event_title`, `event_type`, `department`, `semester`, `start_date`, `end_date`, `venue`, `description`) VALUES
('Semester Orientation Program', 'College Event', 'All Departments', 'Semester 1', CURDATE(), CURDATE(), 'Main Auditorium', 'Welcoming first semester MCA students and introducing college faculty and campus amenities.'),
('Mid-Semester Internal Examination', 'Internal Exam', 'Computer Applications (MCA)', 'Semester 2', DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Exam Hall B', 'Mid-semester assessment covering Units 1, 2, and 3.'),
('National Seminar on Cloud Computing & AI', 'Seminar', 'Computer Applications (MCA)', 'All Semesters', DATE_ADD(CURDATE(), INTERVAL 15 DAY), DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'Seminar Hall 1', 'Expert lectures by industry experts on cloud infrastructure and artificial intelligence applications.'),
('National Youth Day Holiday', 'Holiday', 'All Departments', 'All Semesters', DATE_ADD(CURDATE(), INTERVAL 20 DAY), DATE_ADD(CURDATE(), INTERVAL 20 DAY), 'N/A', 'College holiday on account of National Youth Day.'),
('End-Semester Practical Examinations', 'Semester Exam', 'Computer Science', 'Semester 4', DATE_ADD(CURDATE(), INTERVAL 30 DAY), DATE_ADD(CURDATE(), INTERVAL 35 DAY), 'Computer Lab 3', 'Practical lab examinations for Web Development and Database Lab.');
