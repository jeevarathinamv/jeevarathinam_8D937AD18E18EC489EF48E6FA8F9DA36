-- College Hostel Room Allocation System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `hostel_db`;
USE `hostel_db`;

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

-- Table structure for rooms
CREATE TABLE IF NOT EXISTS `rooms` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `room_number` VARCHAR(20) NOT NULL,
    `hostel_name` VARCHAR(100) NOT NULL,
    `room_type` VARCHAR(20) NOT NULL, -- Single, Double, Triple
    `capacity` INT NOT NULL,
    `available_beds` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for allocations
CREATE TABLE IF NOT EXISTS `allocations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `room_id` INT NOT NULL,
    `allocation_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Allocated', -- Allocated, Cancelled
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`room_id`) REFERENCES `rooms`(`id`) ON DELETE CASCADE
);

-- Seed initial default admin user (username: admin, password: admin123)
-- pbkdf2:sha256 hash for 'admin123'
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$uH3dM2q1K98nL75A$0ff828ba39c4aa0ed4ee062bf66418b765ec2bc41ef69c0d9aef649479b18dc84db2ddb03a30c00dbf9bbec1b2ba278ec642ec346f00dd2f974eb3cf72bd7e7a')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed initial sample rooms
INSERT INTO `rooms` (`room_number`, `hostel_name`, `room_type`, `capacity`, `available_beds`) VALUES
('A-101', 'Boys Hostel Block A', 'Single', 1, 1),
('A-102', 'Boys Hostel Block A', 'Double', 2, 2),
('A-103', 'Boys Hostel Block A', 'Triple', 3, 3),
('B-201', 'Girls Hostel Block B', 'Single', 1, 1),
('B-202', 'Girls Hostel Block B', 'Double', 2, 2);
