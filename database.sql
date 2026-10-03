-- Student Assignment Submission & Deadline Tracker Database Schema
-- Database Name: student_assignment_db

CREATE DATABASE IF NOT EXISTS `student_assignment_db`;
USE `student_assignment_db`;

-- Table structure for `students`
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for `admins`
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for `assignments`
CREATE TABLE IF NOT EXISTS `assignments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `subject` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `given_date` DATE NOT NULL,
    `deadline_date` DATE NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table structure for `submissions`
CREATE TABLE IF NOT EXISTS `submissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `assignment_id` INT NOT NULL,
    `student_id` INT NOT NULL,
    `student_register_number` VARCHAR(50) NOT NULL,
    `submission_date` DATETIME NOT NULL,
    `submission_text` TEXT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Submitted',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`assignment_id`) REFERENCES `assignments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sample Seed Data
-- Note: Password hash corresponds to 'admin123' for admin and 'student123' for student
INSERT INTO `admins` (`id`, `username`, `email`, `password_hash`) VALUES
(1, 'admin', 'admin@college.edu', 'scrypt:32768:8:1$7Uv9YkO01bM59jpx$3c5ec82e1c94411fbceb15c9ff8bc5bc3b94aeb53ca8cb5ed83dca0d7bd1c65b1d9c9b4e7e6e30b80df8f4a1fae019c00b05b3310037f44d18fa220712218ff1')
ON DUPLICATE KEY UPDATE `username`=`username`;

INSERT INTO `assignments` (`id`, `title`, `subject`, `description`, `given_date`, `deadline_date`) VALUES
(1, 'Flask Web Architecture & Routing', 'Web Technologies', 'Build a simple multi-route web application using Python Flask and Werkzeug routing.', CURDATE() - INTERVAL 5 DAY, CURDATE() + INTERVAL 5 DAY),
(2, 'Database Normalization & ER Diagrams', 'Database Management Systems', 'Explain 1NF, 2NF, 3NF, and BCNF with real-world examples and entity-relationship diagrams.', CURDATE() - INTERVAL 3 DAY, CURDATE() + INTERVAL 1 DAY),
(3, 'Data Structures: Tree Traversals', 'Data Structures & Algorithms', 'Implement In-order, Pre-order, and Post-order traversals in Python with time complexity analysis.', CURDATE() - INTERVAL 10 DAY, CURDATE() - INTERVAL 2 DAY)
ON DUPLICATE KEY UPDATE `title`=`title`;
