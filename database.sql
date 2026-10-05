-- ====================================================================
-- Hostel Room Change Request System
-- Database Schema for MySQL / XAMPP phpMyAdmin
-- ====================================================================

/*
XAMPP / phpMyAdmin Setup Instructions:
--------------------------------------------------------------------
1. Start XAMPP Control Panel and start Apache and MySQL services.
2. Open your web browser and go to http://localhost/phpmyadmin/
3. Click on the "SQL" tab.
4. Copy and paste the contents of this file into the SQL query box.
5. Click "Go" to execute the script and create the database and tables.

VS Code Run Steps:
--------------------------------------------------------------------
1. Open the project folder in VS Code.
2. Open terminal in VS Code (Ctrl + `).
3. Install dependencies:
   pip install -r requirements.txt
4. Run the Flask application:
   python app.py
5. Open browser at http://127.0.0.1:5000/

Default Credentials:
--------------------------------------------------------------------
Admin Username: admin
Admin Password: admin123
*/

CREATE DATABASE IF NOT EXISTS `hostel_room_change_db`;
USE `hostel_room_change_db`;

-- 1. Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) NOT NULL UNIQUE,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table structure for rooms
CREATE TABLE IF NOT EXISTS `rooms` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `room_number` VARCHAR(20) NOT NULL UNIQUE,
    `hostel_name` VARCHAR(100) NOT NULL,
    `room_type` VARCHAR(50) NOT NULL,
    `capacity` INT NOT NULL DEFAULT 2,
    `available_beds` INT NOT NULL DEFAULT 2,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Table structure for room_allocations
CREATE TABLE IF NOT EXISTS `room_allocations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `room_id` INT NOT NULL,
    `allocation_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Active',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`room_id`) REFERENCES `rooms`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Table structure for room_change_requests
CREATE TABLE IF NOT EXISTS `room_change_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `request_id` VARCHAR(50) NOT NULL UNIQUE,
    `student_id` INT NOT NULL,
    `current_room_id` INT DEFAULT NULL,
    `requested_room_id` INT NOT NULL,
    `reason` VARCHAR(100) NOT NULL,
    `request_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending',
    `admin_remarks` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`current_room_id`) REFERENCES `rooms`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`requested_room_id`) REFERENCES `rooms`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed Default Admin Account (Username: admin, Password: admin123)
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$ufyNgUwTayhK89mS$336e05bce70bc72cdf50bfd2c4484ad171ff967493c755e5edb1bae232c88bb01f1d780a33313e07f34d9bd3086c443401ee42ba7dc3e9e67c02572ab0af4890')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Sample Rooms
INSERT INTO `rooms` (`room_number`, `hostel_name`, `room_type`, `capacity`, `available_beds`) VALUES
('101', 'A Block Hostel', 'Double', 2, 1),
('102', 'A Block Hostel', 'Single', 1, 1),
('201', 'B Block Hostel', 'Triple', 3, 2),
('202', 'B Block Hostel', 'Double', 2, 2),
('301', 'C Block Hostel', 'Single', 1, 0)
ON DUPLICATE KEY UPDATE `id`=`id`;
