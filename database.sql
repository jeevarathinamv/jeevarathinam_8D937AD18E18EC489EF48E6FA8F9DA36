-- Student Skill Workshop Management Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `student_skill_workshop`;
USE `student_skill_workshop`;

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

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for workshops
CREATE TABLE IF NOT EXISTS `workshops` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(150) NOT NULL,
    `description` TEXT,
    `category` VARCHAR(50) NOT NULL,
    `trainer_name` VARCHAR(100) NOT NULL,
    `date` DATE NOT NULL,
    `time` VARCHAR(50) NOT NULL,
    `venue` VARCHAR(150) NOT NULL,
    `total_seats` INT NOT NULL DEFAULT 30,
    `available_seats` INT NOT NULL DEFAULT 30,
    `status` VARCHAR(20) DEFAULT 'Upcoming',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for registrations
CREATE TABLE IF NOT EXISTS `registrations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `workshop_id` INT NOT NULL,
    `registration_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Registered',
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`workshop_id`) REFERENCES `workshops`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_student_workshop` (`student_id`, `workshop_id`)
);

-- Seed Default Admin User (username: admin, password: admin123)
-- scrypt hash for 'admin123' or app handles fallback / seed
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$m9...$admin123_hash')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed Sample Workshops
INSERT INTO `workshops` (`title`, `description`, `category`, `trainer_name`, `date`, `time`, `venue`, `total_seats`, `available_seats`, `status`) VALUES
('Mastering Python & Flask', 'Hands-on workshop covering Python fundamentals and web applications with Flask.', 'Python', 'Prof. Ramesh Kumar', '2025-05-15', '10:00 AM - 01:00 PM', 'Seminar Hall A', 40, 40, 'Upcoming'),
('Modern Web Development with Bootstrap 5', 'Learn responsive frontend design, HTML5, CSS3, and Bootstrap 5 utilities.', 'Web Development', 'Dr. Priya Sharma', '2025-05-20', '02:00 PM - 05:00 PM', 'Computer Lab 2', 35, 35, 'Upcoming'),
('Java Enterprise Concepts', 'Deep dive into Core Java, OOP principles, and basic enterprise architecture.', 'Java', 'Prof. Anita Roy', '2025-05-25', '11:00 AM - 02:00 PM', 'Seminar Hall B', 50, 50, 'Upcoming'),
('MySQL Database Design & Query Optimization', 'Learn relational database modeling, normalization, SQL queries, and indexing.', 'Database', 'Dr. K. V. Sundaram', '2025-06-01', '09:30 AM - 12:30 PM', 'Computer Lab 1', 30, 30, 'Upcoming'),
('Data Science Fundamentals using Python', 'Introduction to NumPy, Pandas, Data Analysis, and visualization techniques.', 'Data Science', 'Dr. Suresh Nair', '2025-06-10', '10:00 AM - 04:00 PM', 'Auditorium', 60, 60, 'Upcoming'),
('Effective Business Communication', 'Interactive workshop on verbal communication, professional writing, and public speaking.', 'Communication', 'Prof. Meera Menen', '2025-06-15', '02:00 PM - 04:00 PM', 'Seminar Hall A', 45, 45, 'Upcoming'),
('Soft Skills & Interview Preparation', 'Resume building, group discussion tactics, and mock interview practice.', 'Soft Skills', 'Mr. Vikram Verma', '2025-06-20', '10:00 AM - 01:00 PM', 'Placement Cell', 50, 50, 'Upcoming');
