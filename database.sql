-- Campus Recruitment Drive Registration System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `campus_recruitment`;
USE `campus_recruitment`;

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `phone_number` VARCHAR(20) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for recruitment_drives
CREATE TABLE IF NOT EXISTS `recruitment_drives` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_name` VARCHAR(150) NOT NULL,
    `job_role` VARCHAR(100) NOT NULL,
    `eligibility` VARCHAR(200) NOT NULL,
    `package` VARCHAR(100) NOT NULL,
    `drive_date` DATE NOT NULL,
    `location` VARCHAR(150) NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for registrations
CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `drive_id` INT NOT NULL,
    `registration_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Registered', -- Registered, Shortlisted, Selected, Rejected
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_student_drive` (`student_id`, `drive_id`),
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`drive_id`) REFERENCES `recruitment_drives`(`id`) ON DELETE CASCADE
);

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial sample recruitment drives
INSERT INTO `recruitment_drives` (`company_name`, `job_role`, `eligibility`, `package`, `drive_date`, `location`, `description`) VALUES
('TechCorp Solutions', 'Software Development Engineer', 'B.Tech CS/IT, MCA with 60%+', '$12,000 / 8 LPA', DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Main Campus Auditorium', 'Full-stack software development role focusing on Python, Flask, and React.'),
('DataViz Innovations', 'Data Analyst', 'All B.E / B.Tech / B.Sc / MCA graduates', '$10,000 / 6.5 LPA', DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'Virtual / Zoom', 'Analyzing large datasets, writing SQL queries, and creating visual BI dashboards.'),
('CloudNet Systems', 'DevOps & Cloud Trainee', 'CS / IT / ECE graduates', '$11,000 / 7 LPA', DATE_ADD(CURDATE(), INTERVAL 20 DAY), 'Tech Park Block B', 'Deployment automation, Docker containerization, and AWS cloud management.');
