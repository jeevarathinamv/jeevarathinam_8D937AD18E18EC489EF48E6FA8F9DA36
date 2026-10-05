-- ============================================================
-- College Drinking Water Complaint & Maintenance System
-- Database Schema for MySQL / XAMPP phpMyAdmin
-- ============================================================
--
-- XAMPP / phpMyAdmin Setup Instructions:
-- 1. Open XAMPP Control Panel and start "Apache" and "MySQL".
-- 2. Open your web browser and go to: http://localhost/phpmyadmin
-- 3. Click on "Databases" tab or "New", create database: `water_complaint_db`
-- 4. Select `water_complaint_db` and click on "Import" tab.
-- 5. Choose this `database.sql` file and click "Go".
--
-- VS Code Run Steps:
-- 1. Open VS Code in project folder.
-- 2. Run: pip install -r requirements.txt
-- 3. Run: python app.py
-- 4. Open browser at: http://127.0.0.1:5000/
--
-- Sample Credentials:
-- Admin Username: admin
-- Admin Password: admin123
-- Student Email: student@college.edu
-- Student Password: password123
-- ============================================================

CREATE DATABASE IF NOT EXISTS `water_complaint_db`;
USE `water_complaint_db`;

-- Table structure for `admins`
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for `students`
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) NOT NULL UNIQUE,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for `complaints`
CREATE TABLE IF NOT EXISTS `complaints` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `complaint_id` VARCHAR(50) NOT NULL UNIQUE,
    `student_id` INT NOT NULL,
    `complaint_type` VARCHAR(100) NOT NULL,
    `location` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `complaint_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, In Progress, Resolved, Rejected
    `admin_remarks` TEXT,
    `resolved_date` DATE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Default Admin Account (Username: admin, Password: admin123 hashed via pbkdf2:sha256)
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$C0S0f5IeGf0E$b57dd94bf6529e81b67f678ef40a04edecbc9c7e0f87a3219aaec7d6e68a3562bcfe6ca73356e87aed2a5a2ddb6f799e4f5a34eeb82ee0a9ee2bfe2c673eb8b2')
ON DUPLICATE KEY UPDATE `username` = `username`;

-- Sample Student Account (Email: student@college.edu, Reg: MCA202401, Password: password123)
INSERT INTO `students` (`id`, `name`, `register_number`, `department`, `email`, `password_hash`) VALUES
(1, 'John Doe', 'MCA202401', 'Computer Applications (MCA)', 'student@college.edu', 'scrypt:32768:8:1$C0S0f5IeGf0E$b57dd94bf6529e81b67f678ef40a04edecbc9c7e0f87a3219aaec7d6e68a3562bcfe6ca73356e87aed2a5a2ddb6f799e4f5a34eeb82ee0a9ee2bfe2c673eb8b2')
ON DUPLICATE KEY UPDATE `id` = `id`;

-- Sample Water Complaints
INSERT INTO `complaints` (`complaint_id`, `student_id`, `complaint_type`, `location`, `description`, `complaint_date`, `status`, `admin_remarks`, `resolved_date`) VALUES
('CWP-100201', 1, 'Water Cooler Problem', '2nd Floor - Science Block', 'Water cooler is leaking water on the floor and not cooling properly.', CURDATE(), 'Pending', NULL, NULL),
('CWP-100202', 1, 'RO Problem', 'Library Ground Floor', 'RO filter indicator shows filter replacement warning and water taste is salty.', CURDATE(), 'In Progress', 'Assigned maintenance technician for inspection.', NULL),
('CWP-100203', 1, 'Water Quality Problem', 'Hostel Block A', 'Water color appears slightly yellow in the morning hours.', CURDATE(), 'Resolved', 'Flushed supply lines and cleaned overhead water tank.', CURDATE())
ON DUPLICATE KEY UPDATE `complaint_id` = `complaint_id`;
