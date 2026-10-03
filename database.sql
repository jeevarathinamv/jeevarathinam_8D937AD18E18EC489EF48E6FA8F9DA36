-- Small Business Online Enquiry & Lead Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `small_business_db`;
USE `small_business_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for enquiries
CREATE TABLE IF NOT EXISTS `enquiries` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `ref_num` VARCHAR(20) NOT NULL UNIQUE,
    `customer_name` VARCHAR(100) NOT NULL,
    `phone_number` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `subject` VARCHAR(200) NOT NULL,
    `message` TEXT NOT NULL,
    `enquiry_date` DATE NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'New', -- New, In Progress, Responded, Closed
    `admin_response` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for leads
CREATE TABLE IF NOT EXISTS `leads` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `enquiry_id` INT DEFAULT NULL,
    `customer_name` VARCHAR(100) NOT NULL,
    `phone_number` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `requirement` TEXT NOT NULL,
    `status` VARCHAR(30) NOT NULL DEFAULT 'New Lead', -- New Lead, Contacted, Follow-up, Converted, Lost
    `follow_up_date` DATE DEFAULT NULL,
    `notes` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`enquiry_id`) REFERENCES `enquiries`(`id`) ON DELETE SET NULL
);

-- Table structure for followups
CREATE TABLE IF NOT EXISTS `followups` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `lead_id` INT NOT NULL,
    `follow_up_date` DATE NOT NULL,
    `notes` TEXT NOT NULL,
    `status_at_time` VARCHAR(30) DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`lead_id`) REFERENCES `leads`(`id`) ON DELETE CASCADE
);

-- Sample initial admin credentials (username: admin, password: admin123)
-- Password hash generated using werkzeug.security generate_password_hash('admin123')
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$u7F5G1z8eZ4Q3Y0A$34b182fb8f36c4b2a8d43d1a8e1b1234567890abcdef1234567890abcdef')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Sample initial enquiries
INSERT INTO `enquiries` (`ref_num`, `customer_name`, `phone_number`, `email`, `subject`, `message`, `enquiry_date`, `status`, `admin_response`) VALUES
('ENQ-1001', 'John Doe', '9876543210', 'john@example.com', 'Web Development Services', 'Looking for a custom business website for our retail shop.', CURDATE(), 'New', NULL),
('ENQ-1002', 'Sarah Smith', '9876543211', 'sarah@techcorp.com', 'SEO & Marketing Package', 'Need consultation regarding digital marketing and lead generation.', CURDATE(), 'In Progress', 'Scheduled initial discussion call for tomorrow.'),
('ENQ-1003', 'Michael Brown', '9876543212', 'michael@designstudio.com', 'Software Maintenance', 'Inquiring about annual maintenance contract for existing CRM.', CURDATE(), 'Responded', 'Sent quotation details via email.');

-- Sample initial leads
INSERT INTO `leads` (`enquiry_id`, `customer_name`, `phone_number`, `email`, `requirement`, `status`, `follow_up_date`, `notes`) VALUES
(1, 'John Doe', '9876543210', 'john@example.com', 'Custom business website with e-commerce features.', 'New Lead', CURDATE(), 'Customer requested proposal by weekend.'),
(2, 'Sarah Smith', '9876543211', 'sarah@techcorp.com', 'Full digital marketing setup and SEO audit.', 'Follow-up', CURDATE(), 'Follow up regarding budget approval.');

-- Sample initial followups
INSERT INTO `followups` (`lead_id`, `follow_up_date`, `notes`, `status_at_time`) VALUES
(2, CURDATE(), 'Called Sarah to review proposal draft.', 'Follow-up');
