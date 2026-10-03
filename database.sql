-- Service Business Booking & Customer Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `service_booking_db`;
USE `service_booking_db`;

-- 1. Table structure for Admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `name` VARCHAR(100) NOT NULL DEFAULT 'Administrator',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table structure for Customers
CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table structure for Services
CREATE TABLE IF NOT EXISTS `services` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `price` DOUBLE NOT NULL,
    `duration` VARCHAR(50) NOT NULL,
    `availability` VARCHAR(50) NOT NULL DEFAULT 'Available',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table structure for Bookings
CREATE TABLE IF NOT EXISTS `bookings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `service_id` INT NOT NULL,
    `booking_date` DATE NOT NULL,
    `booking_time` VARCHAR(20) NOT NULL,
    `customer_name` VARCHAR(100) NOT NULL,
    `customer_phone` VARCHAR(20) NOT NULL,
    `notes` TEXT,
    `status` VARCHAR(20) NOT NULL DEFAULT 'Pending', -- Pending, Confirmed, Completed, Cancelled
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`service_id`) REFERENCES `services`(`id`) ON DELETE CASCADE
);

-- Default Admin Account (Username: admin | Password hash for admin123)
INSERT INTO `admins` (`username`, `password_hash`, `name`) VALUES
('admin', 'scrypt:32768:8:1$7Ua1Ie6pM5pEaU2Z$fbd8eaeeaa1bfa3c61ae060933f7ccfa89c09641775fefbb5dcf85b2e3e5bfdc1e089209dbbe4ca707887713d875a5b51b3a56ad9ca11494ae6d2cae2c2193b2', 'System Administrator')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Initial Sample Services
INSERT INTO `services` (`name`, `description`, `price`, `duration`, `availability`) VALUES
('Deep House Cleaning', 'Comprehensive deep cleaning service for home bedrooms, kitchen, living room, and bathrooms.', 89.99, '3 Hours', 'Available'),
('AC Maintenance & Repair', 'Complete air conditioner inspection, filter cleaning, refrigerant refill, and cooling test.', 49.99, '1.5 Hours', 'Available'),
('Car Wash & Detailing', 'Premium exterior eco-wash, interior vacuuming, dashboard polish, and tire shining.', 35.00, '1 Hour', 'Available'),
('Plumbing Repair & Inspection', 'Fixing pipe leaks, tap installations, drain cleaning, and water pressure checks.', 55.00, '2 Hours', 'Available'),
('Electrical Safety Audit & Fix', 'Wiring inspection, circuit breaker repair, switch installation, and electrical troubleshooting.', 60.00, '2 Hours', 'Available');
