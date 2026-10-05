-- Student Exam Timetable Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `exam_timetable_db`;
USE `exam_timetable_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL
);

-- Table structure for students
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) UNIQUE NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) UNIQUE NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for exam_timetable
CREATE TABLE IF NOT EXISTS `exam_timetable` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `exam_name` VARCHAR(100) NOT NULL,
    `department` VARCHAR(100) NOT NULL,
    `semester` VARCHAR(20) NOT NULL,
    `subject_name` VARCHAR(100) NOT NULL,
    `subject_code` VARCHAR(50) NOT NULL,
    `exam_date` DATE NOT NULL,
    `exam_time` VARCHAR(50) NOT NULL,
    `exam_venue` VARCHAR(100) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed default admin credentials (Username: admin, Password: admin123)
-- Password stored using Werkzeug pbkdf2:sha256 hash
INSERT INTO `admins` (`username`, `password`) VALUES
('admin', 'scrypt:32768:8:1$uR9eF1A8sL!$9f471e42c23946279f64839cf9e58319f39446d3e339d22cf2c7e0965c2df910')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed sample exam timetable records for MCA student demonstration
INSERT INTO `exam_timetable` (`exam_name`, `department`, `semester`, `subject_name`, `subject_code`, `exam_date`, `exam_time`, `exam_venue`) VALUES
('End Semester Examinations - May 2025', 'Master of Computer Applications (MCA)', 'Semester 1', 'Data Structures and Algorithms', 'MCA101', '2025-05-12', '10:00 AM - 01:00 PM', 'Lab Hall A (Ground Floor)'),
('End Semester Examinations - May 2025', 'Master of Computer Applications (MCA)', 'Semester 1', 'Database Management Systems', 'MCA102', '2025-05-14', '10:00 AM - 01:00 PM', 'Main Exam Hall 2'),
('End Semester Examinations - May 2025', 'Master of Computer Applications (MCA)', 'Semester 1', 'Python Web Development with Flask', 'MCA103', '2025-05-16', '10:00 AM - 01:00 PM', 'Computer Lab 3'),
('End Semester Examinations - May 2025', 'Master of Computer Applications (MCA)', 'Semester 2', 'Advanced Java & Enterprise Applications', 'MCA201', '2025-05-13', '02:00 PM - 05:00 PM', 'Main Exam Hall 1'),
('End Semester Examinations - May 2025', 'Master of Computer Applications (MCA)', 'Semester 2', 'Cloud Computing & DevOps', 'MCA202', '2025-05-15', '02:00 PM - 05:00 PM', 'Seminar Hall B'),
('Mid Term Examinations - March 2025', 'Department of Information Technology', 'Semester 1', 'Software Engineering & Agile Methodologies', 'IT101', '2025-03-20', '10:00 AM - 12:00 PM', 'IT Block Hall 101');
