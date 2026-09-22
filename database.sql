-- Student Study Partner Finder
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_study_partner`;
USE `student_study_partner`;

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

-- Table structure for profiles
CREATE TABLE IF NOT EXISTS `profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNIQUE NOT NULL,
    `subjects` VARCHAR(255) DEFAULT '',
    `skills` VARCHAR(255) DEFAULT '',
    `preferred_study_time` VARCHAR(100) DEFAULT 'Flexible',
    `study_mode` VARCHAR(50) DEFAULT 'Hybrid',
    `short_bio` TEXT,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for partner_requests
CREATE TABLE IF NOT EXISTS `partner_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sender_id` INT NOT NULL,
    `receiver_id` INT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Accepted, Rejected
    `message` VARCHAR(255) DEFAULT '',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`sender_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`receiver_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial admin account (Default: admin / admin123)
-- Password hash generated using scrypt / pbkdf2 werkzeug default for admin123
INSERT INTO `admins` (`username`, `password_hash`, `email`) VALUES
('admin', 'scrypt:32768:8:1$uM6Wk2Y64516E49i$00418c39eef7655bcbfceaa1360cf2b2d6ff3b99fe11adbc5c4b8e8f8ce0ca88aa0b31e13cb4fe4b12aa1c6aa1bd533d11bbfed1eb1a478bcfb5c00b0f4fa6e8', 'admin@studypartner.com')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed sample students
INSERT INTO `students` (`id`, `name`, `register_number`, `department`, `email`, `password_hash`) VALUES
(1, 'Aarav Sharma', 'REG202401', 'Computer Science', 'aarav@example.com', 'scrypt:32768:8:1$uM6Wk2Y64516E49i$00418c39eef7655bcbfceaa1360cf2b2d6ff3b99fe11adbc5c4b8e8f8ce0ca88aa0b31e13cb4fe4b12aa1c6aa1bd533d11bbfed1eb1a478bcfb5c00b0f4fa6e8'),
(2, 'Ananya Patel', 'REG202402', 'Information Technology', 'ananya@example.com', 'scrypt:32768:8:1$uM6Wk2Y64516E49i$00418c39eef7655bcbfceaa1360cf2b2d6ff3b99fe11adbc5c4b8e8f8ce0ca88aa0b31e13cb4fe4b12aa1c6aa1bd533d11bbfed1eb1a478bcfb5c00b0f4fa6e8'),
(3, 'Rohan Verma', 'REG202403', 'Computer Applications (MCA)', 'rohan@example.com', 'scrypt:32768:8:1$uM6Wk2Y64516E49i$00418c39eef7655bcbfceaa1360cf2b2d6ff3b99fe11adbc5c4b8e8f8ce0ca88aa0b31e13cb4fe4b12aa1c6aa1bd533d11bbfed1eb1a478bcfb5c00b0f4fa6e8')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed sample student profiles
INSERT INTO `profiles` (`student_id`, `subjects`, `skills`, `preferred_study_time`, `study_mode`, `short_bio`) VALUES
(1, 'Python, Data Structures, Algorithms', 'Python, C++, SQL', 'Evening (5 PM - 8 PM)', 'Online', 'Passionate about algorithm problem solving and web development. Looking for serious study partner.'),
(2, 'Database Management, Web Technologies', 'HTML/CSS, JavaScript, MySQL', 'Morning (8 AM - 12 PM)', 'Hybrid', 'Enthusiastic front-end developer eager to collaborate on full-stack web projects.'),
(3, 'Machine Learning, Artificial Intelligence, Python', 'Python, Data Analysis, PyTorch', 'Night (8 PM - 11 PM)', 'Offline', 'MCA student preparing for campus placements. Love discussing AI concept questions.')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed sample partner request
INSERT INTO `partner_requests` (`sender_id`, `receiver_id`, `status`, `message`) VALUES
(1, 2, 'Pending', 'Hi Ananya! Let us study Web Development and Database Management together.')
ON DUPLICATE KEY UPDATE `id`=`id`;
