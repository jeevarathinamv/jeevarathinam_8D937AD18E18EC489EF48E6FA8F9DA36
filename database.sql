-- Lab Computer Fault Reporting System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `lab_computer_fault_db`;
USE `lab_computer_fault_db`;

-- Table 1: Admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table 2: Students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table 3: Computers
CREATE TABLE IF NOT EXISTS `computers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `computer_number` VARCHAR(50) NOT NULL,
    `lab_name` VARCHAR(100) NOT NULL,
    `computer_name` VARCHAR(100) NOT NULL,
    `ip_address` VARCHAR(50) NOT NULL,
    `status` VARCHAR(50) DEFAULT 'Working'
);

-- Table 4: Fault Reports
CREATE TABLE IF NOT EXISTS `fault_reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `complaint_id` VARCHAR(50) UNIQUE NOT NULL,
    `student_id` INT NOT NULL,
    `computer_id` INT DEFAULT NULL,
    `lab_name` VARCHAR(100) NOT NULL,
    `computer_number` VARCHAR(50) NOT NULL,
    `fault_type` VARCHAR(100) NOT NULL,
    `problem_description` TEXT NOT NULL,
    `report_date` DATE NOT NULL,
    `status` VARCHAR(50) DEFAULT 'Pending',
    `admin_remarks` TEXT DEFAULT NULL,
    `resolved_date` DATE DEFAULT NULL,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`computer_id`) REFERENCES `computers`(`id`) ON DELETE SET NULL
);

-- Insert Default Admin (Username: admin, Password: admin123 hashed using werkzeug PBKDF2 SHA256)
INSERT INTO `admins` (`username`, `password`)
VALUES ('admin', 'scrypt:32768:8:1$uB0GvL8e0iK6a60z$b5f3a0937a07727ff0360a8ea1110f2df98c3619db3dbd394b9f29ee87ef0aa4c330f81d11ff982b6bce75c74384bf3df4aaec2f854beecdd1643c5bdf150824')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed sample computers
INSERT INTO `computers` (`computer_number`, `lab_name`, `computer_name`, `ip_address`, `status`) VALUES
('COMP-101', 'Computer Lab 1', 'Dell OptiPlex 3080', '192.168.1.101', 'Working'),
('COMP-102', 'Computer Lab 1', 'Dell OptiPlex 3080', '192.168.1.102', 'Working'),
('COMP-103', 'Computer Lab 1', 'HP ProDesk 400', '192.168.1.103', 'Faulty'),
('COMP-201', 'MCA Programming Lab', 'Lenovo ThinkCentre', '192.168.2.101', 'Working'),
('COMP-202', 'MCA Programming Lab', 'Lenovo ThinkCentre', '192.168.2.102', 'Under Maintenance');
