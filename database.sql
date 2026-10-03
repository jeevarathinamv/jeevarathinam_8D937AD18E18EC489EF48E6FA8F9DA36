-- Student Project Showcase Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_project_showcase`;
USE `student_project_showcase`;

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for projects
CREATE TABLE IF NOT EXISTS `projects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `description` TEXT NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `technologies` VARCHAR(200) NOT NULL,
    `image_path` VARCHAR(255) DEFAULT NULL,
    `project_link` VARCHAR(255) DEFAULT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Approved, Rejected
    `admin_remark` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert Default Admin Account (Username: admin, Password: admin123)
-- Password hash generated via Werkzeug security
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$yF84XvX2U9v3Cj4l$0e8fa358245cd9a77efb3ef657732a3737cb2f4dd8a32a68c430e7137f7a8ba3fb9e9f9bb5ef91e4a64d6023ea0be712be17e1320efbcfc23940c66d2a8435d8')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Insert Sample Student
INSERT INTO `students` (`name`, `register_number`, `department`, `email`, `password_hash`) VALUES
('Rahul Sharma', 'MCA202401', 'Computer Applications (MCA)', 'rahul@college.edu', 'scrypt:32768:8:1$yF84XvX2U9v3Cj4l$0e8fa358245cd9a77efb3ef657732a3737cb2f4dd8a32a68c430e7137f7a8ba3fb9e9f9bb5ef91e4a64d6023ea0be712be17e1320efbcfc23940c66d2a8435d8')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Insert Sample Projects
INSERT INTO `projects` (`student_id`, `title`, `description`, `category`, `technologies`, `project_link`, `status`, `admin_remark`) VALUES
(1, 'E-Commerce Analytics Dashboard', 'A real-time analytics web dashboard that visualizes store sales, customer retention rates, and top performing product categories with interactive charts.', 'Web Development', 'Python, Flask, Chart.js, Bootstrap 5, MySQL', 'https://github.com/example/ecommerce-analytics', 'Approved', 'Great project structure and visual representation.'),
(1, 'AI Powered Code Explainer', 'An interactive desktop tool that parses Python and Java source code to build abstract syntax trees and output clear natural language explanations.', 'Python', 'Python, Tkinter, AST, PyInstaller', 'https://github.com/example/code-explainer', 'Pending', NULL);
