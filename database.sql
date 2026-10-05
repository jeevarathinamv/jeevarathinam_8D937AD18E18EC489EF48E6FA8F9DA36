-- Student Semester Course Registration Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_course_registration`;
USE `student_course_registration`;

-- 1. Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `year` INT NOT NULL,
    `semester` INT NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table structure for courses
CREATE TABLE IF NOT EXISTS `courses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `course_name` VARCHAR(100) NOT NULL,
    `course_code` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `semester` INT NOT NULL,
    `course_type` VARCHAR(50) NOT NULL, -- Core, Elective, Practical
    `credits` INT NOT NULL DEFAULT 3,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table structure for registrations
CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `course_id` INT NOT NULL,
    `registration_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Registered', -- Registered, Cancelled
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE
);

-- Seed default admin user (Username: admin, Password: admin123)
-- Password hash corresponds to 'admin123'
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$uJ8n3x9Z$c7a3328f4142d1743e34b92b58832a82d02919c67ed19c8d0a84e6bd54a5c92e10dbbe8d715915d311d4e0ebf96d073845b5e7d4ee6b6805178bd302f30b91e9')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed sample courses
INSERT INTO `courses` (`course_name`, `course_code`, `department`, `semester`, `course_type`, `credits`) VALUES
('Advanced Java Programming', 'MCA101', 'Computer Applications (MCA)', 1, 'Core', 4),
('Database Management Systems', 'MCA102', 'Computer Applications (MCA)', 1, 'Core', 4),
('Web Technologies Lab', 'MCA103', 'Computer Applications (MCA)', 1, 'Practical', 2),
('Software Engineering', 'MCA104', 'Computer Applications (MCA)', 1, 'Elective', 3),
('Python Web Development', 'MCA201', 'Computer Applications (MCA)', 2, 'Core', 4),
('Data Science & Analytics', 'MCA202', 'Computer Applications (MCA)', 2, 'Core', 4),
('Cloud Computing Lab', 'MCA203', 'Computer Applications (MCA)', 2, 'Practical', 2);
