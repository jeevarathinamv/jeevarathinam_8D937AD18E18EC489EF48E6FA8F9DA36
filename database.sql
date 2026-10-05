-- Student Subject Registration System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `subject_registration_db`;
USE `subject_registration_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` INT NOT NULL,
    `semester` INT NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for subjects
CREATE TABLE IF NOT EXISTS `subjects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_name` VARCHAR(100) NOT NULL,
    `subject_code` VARCHAR(20) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `semester` INT NOT NULL,
    `subject_type` VARCHAR(20) NOT NULL, -- Core, Elective, Practical
    `credits` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for registrations
CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `registration_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Registered', -- Registered, Cancelled
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE
);

-- Seed initial admin user
INSERT INTO `admins` (`username`, `password`) VALUES
('admin', 'scrypt:32768:8:1$default_admin_hash_or_similar')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed sample subjects for Computer Applications (MCA)
INSERT INTO `subjects` (`subject_name`, `subject_code`, `department`, `semester`, `subject_type`, `credits`) VALUES
('Advanced Java Programming', 'MCA101', 'Computer Applications', 1, 'Core', 4),
('Database Management Systems', 'MCA102', 'Computer Applications', 1, 'Core', 4),
('Web Technologies Lab', 'MCA103', 'Computer Applications', 1, 'Practical', 2),
('Cloud Computing', 'MCA104', 'Computer Applications', 1, 'Elective', 3),
('Python Application Programming', 'MCA201', 'Computer Applications', 2, 'Core', 4),
('Data Structures and Algorithms', 'MCA202', 'Computer Applications', 2, 'Core', 4),
('Software Engineering Lab', 'MCA203', 'Computer Applications', 2, 'Practical', 2),
('Cyber Security & Cyber Laws', 'MCA204', 'Computer Applications', 2, 'Elective', 3)
ON DUPLICATE KEY UPDATE `subject_code`=`subject_code`;
