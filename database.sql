-- College Department Information Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `department_db`;
USE `department_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` VARCHAR(50) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for department
CREATE TABLE IF NOT EXISTS `department` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `code` VARCHAR(20) NOT NULL,
    `head` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `description` TEXT NOT NULL
);

-- Table structure for faculty
CREATE TABLE IF NOT EXISTS `faculty` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `faculty_id` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `designation` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for notices
CREATE TABLE IF NOT EXISTS `notices` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `notice_date` DATE NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial admin user (username: admin, password: admin123)
-- Password hash generated using werkzeug.security.generate_password_hash('admin123')
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$73rI0GqWkX$c72836e1c251d1f0ffc4033b00609b53cf5f8e58fbe6c4669f64bf50cf41f87c2cbeae6bb7bb8f1d8c11e3b62ca7ef66e133544793f7bcbd4b01e40b6e9a6e35')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed default department information
INSERT INTO `department` (`id`, `name`, `code`, `head`, `email`, `phone`, `description`) VALUES
(1, 'Department of Computer Applications', 'MCA-DEPT', 'Dr. S. Ramanathan', 'mca.dept@college.edu', '+91 98765 43210', 'The Department of Computer Applications is committed to excellence in computer science education, practical software development skills, and modern technology research.')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed sample faculty members
INSERT INTO `faculty` (`name`, `faculty_id`, `department`, `designation`, `email`, `phone`) VALUES
('Dr. S. Ramanathan', 'FAC101', 'Computer Applications', 'Head of Department & Professor', 'ramanathan@college.edu', '+91 98765 43210'),
('Prof. Anita Sharma', 'FAC102', 'Computer Applications', 'Associate Professor', 'anita.sharma@college.edu', '+91 98765 43211'),
('Prof. Rajesh Kumar', 'FAC103', 'Computer Applications', 'Assistant Professor', 'rajesh.kumar@college.edu', '+91 98765 43212');

-- Seed sample notices
INSERT INTO `notices` (`title`, `description`, `notice_date`) VALUES
('Welcome to the New Academic Session', 'Classes for the upcoming semester will commence on Monday. All students are requested to review their updated timetable on the department notice board.', '2025-02-01'),
('Technical Seminar on Web Technologies', 'A special guest lecture on Modern Web Development Frameworks will be conducted in the Main Auditorium at 10:00 AM this Friday.', '2025-02-10'),
('Submission of Project Phase 1 Documentation', 'Final year MCA students are required to submit their Project Phase 1 synopsis and documentation to their respective faculty guides by the end of this week.', '2025-02-15');
