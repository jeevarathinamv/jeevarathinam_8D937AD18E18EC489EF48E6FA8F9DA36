-- College Sports Equipment Booking System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `sports_booking_db`;
USE `sports_booking_db`;

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

-- Table structure for equipment
CREATE TABLE IF NOT EXISTS `equipment` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `total_quantity` INT NOT NULL DEFAULT 0,
    `available_quantity` INT NOT NULL DEFAULT 0,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for bookings
CREATE TABLE IF NOT EXISTS `bookings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `equipment_id` INT NOT NULL,
    `booking_date` DATE NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Approved, Rejected, Returned
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE
);

-- Seed initial equipment items
INSERT INTO `equipment` (`name`, `category`, `total_quantity`, `available_quantity`, `description`) VALUES
('Cricket Bat', 'Cricket', 15, 15, 'English Willow Quality Cricket Bat'),
('Cricket Ball', 'Cricket', 30, 30, 'Standard Red Leather Cricket Ball'),
('Football', 'Football', 20, 20, 'Size 5 Tournament Football'),
('Volleyball', 'Volleyball', 12, 12, 'Official Match Size Volleyball'),
('Volleyball Net', 'Volleyball', 4, 4, 'Durable Nylon Volleyball Net'),
('Badminton Racket', 'Badminton', 25, 25, 'Lightweight Graphite Badminton Racket'),
('Shuttlecocks (Box)', 'Badminton', 15, 15, 'Feather Shuttlecock Box of 10'),
('Basketball', 'Basketball', 10, 10, 'Composite Leather Basketball');
