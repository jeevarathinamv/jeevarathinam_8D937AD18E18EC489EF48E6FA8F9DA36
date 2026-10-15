-- College Attendance & Internal Mark Management System Database Schema
-- Database: college_attendance_db

CREATE DATABASE IF NOT EXISTS `college_attendance_db`;
USE `college_attendance_db`;

-- 1. Admins Table
DROP TABLE IF EXISTS `attendance_records`;
DROP TABLE IF EXISTS `attendance_sessions`;
DROP TABLE IF EXISTS `timetable`;
DROP TABLE IF EXISTS `subjects`;
DROP TABLE IF EXISTS `students`;
DROP TABLE IF EXISTS `classes`;
DROP TABLE IF EXISTS `teachers`;
DROP TABLE IF EXISTS `admins`;
DROP TABLE IF EXISTS `internal_mark_rules`;

CREATE TABLE `admins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Teachers Table
CREATE TABLE `teachers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `teacher_id_code` VARCHAR(50) NOT NULL UNIQUE,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `department` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Classes Table
CREATE TABLE `classes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  `code` VARCHAR(20) NOT NULL UNIQUE,
  `tutor_id` INT DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`tutor_id`) REFERENCES `teachers`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Students Table
CREATE TABLE `students` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `register_number` VARCHAR(50) NOT NULL UNIQUE,
  `name` VARCHAR(100) NOT NULL,
  `class_id` INT NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Subjects Table
CREATE TABLE `subjects` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `code` VARCHAR(20) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `class_id` INT NOT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Timetable Table
CREATE TABLE `timetable` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `class_id` INT NOT NULL,
  `day` VARCHAR(20) NOT NULL,
  `hour_number` INT NOT NULL,
  `subject_id` INT NOT NULL,
  `teacher_id` INT NOT NULL,
  `start_time` VARCHAR(20) DEFAULT '09:00 AM',
  `end_time` VARCHAR(20) DEFAULT '10:00 AM',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_class_day_hour` (`class_id`, `day`, `hour_number`),
  UNIQUE KEY `unique_teacher_day_hour` (`teacher_id`, `day`, `hour_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Attendance Sessions Table
CREATE TABLE `attendance_sessions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `class_id` INT NOT NULL,
  `subject_id` INT NOT NULL,
  `teacher_id` INT NOT NULL,
  `date` DATE NOT NULL,
  `hour_number` INT NOT NULL,
  `timetable_id` INT DEFAULT NULL,
  `submitted_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(20) DEFAULT 'Submitted',
  FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`timetable_id`) REFERENCES `timetable`(`id`) ON DELETE SET NULL,
  UNIQUE KEY `unique_session_class_subject_date_hour` (`class_id`, `subject_id`, `date`, `hour_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Attendance Records Table
CREATE TABLE `attendance_records` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `session_id` INT NOT NULL,
  `student_id` INT NOT NULL,
  `status` VARCHAR(10) NOT NULL, -- 'Present' or 'Absent'
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`session_id`) REFERENCES `attendance_sessions`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `unique_session_student` (`session_id`, `student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Internal Mark Rules Table
CREATE TABLE `internal_mark_rules` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `min_percentage` FLOAT NOT NULL,
  `max_percentage` FLOAT NOT NULL,
  `mark` INT NOT NULL,
  `label` VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Sample Attendance Reports View (Optional Helper View)
CREATE OR REPLACE VIEW `attendance_reports_view` AS
SELECT
  s.id AS student_id,
  s.register_number,
  s.name AS student_name,
  c.id AS class_id,
  c.name AS class_name,
  sub.id AS subject_id,
  sub.name AS subject_name,
  COUNT(ar.id) AS total_hours,
  SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) AS present_hours,
  SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) AS absent_hours,
  ROUND((SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) / COUNT(ar.id)) * 100, 2) AS attendance_percentage
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN subjects sub ON sub.class_id = c.id
LEFT JOIN attendance_sessions se ON se.class_id = c.id AND se.subject_id = sub.id
LEFT JOIN attendance_records ar ON ar.session_id = se.id AND ar.student_id = s.id
GROUP BY s.id, c.id, sub.id;

-- Seed Data Insertion

-- Default Admin (Password: admin123 -> Werkzeug pbkdf2 hash)
INSERT INTO `admins` (`username`, `email`, `password_hash`) VALUES
('admin', 'admin@college.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8');

-- Default Internal Mark Rules
INSERT INTO `internal_mark_rules` (`min_percentage`, `max_percentage`, `mark`, `label`) VALUES
(90.0, 100.0, 5, '5 Marks (Outstanding)'),
(80.0, 89.99, 4, '4 Marks (Very Good)'),
(70.0, 79.99, 3, '3 Marks (Good)'),
(60.0, 69.99, 2, '2 Marks (Satisfactory)'),
(50.0, 59.99, 1, '1 Mark (Pass Margin)'),
(0.0, 49.99, 0, 'RA - Redo Attendance');

-- Teachers
INSERT INTO `teachers` (`teacher_id_code`, `name`, `email`, `department`, `phone`, `password_hash`) VALUES
('TCH101', 'Dr. Aris Thorne', 'aris@college.edu', 'Computer Applications', '9876543210', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('TCH102', 'Prof. Sarah Lin', 'sarah@college.edu', 'Computer Applications', '9876543211', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('TCH103', 'Dr. Rajesh Kumar', 'rajesh@college.edu', 'Computer Applications', '9876543212', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('TCH104', 'Prof. Elena Rostova', 'elena@college.edu', 'Computer Applications', '9876543213', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('TCH105', 'Dr. Michael Chang', 'michael@college.edu', 'Computer Applications', '9876543214', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8');

-- Classes (5 Classes: BCA I, BCA II, BCA III, MCA I, MCA II)
INSERT INTO `classes` (`name`, `code`, `tutor_id`) VALUES
('BCA I', 'BCA1', 1),
('BCA II', 'BCA2', 2),
('BCA III', 'BCA3', 3),
('MCA I', 'MCA1', 4),
('MCA II', 'MCA2', 5);

-- Subjects for Classes
INSERT INTO `subjects` (`code`, `name`, `class_id`) VALUES
('BCA101', 'Programming in C', 1),
('BCA102', 'Digital Fundamentals', 1),
('BCA201', 'Data Structures', 2),
('BCA202', 'Database Systems', 2),
('BCA301', 'Web Technologies', 3),
('BCA302', 'Software Engineering', 3),
('MCA101', 'Python Web Development', 4),
('MCA102', 'Advanced Database Systems', 4),
('MCA201', 'Cloud Computing & DevOps', 5),
('MCA202', 'Artificial Intelligence', 5);

-- Students for Classes (Password for all students: student123)
INSERT INTO `students` (`register_number`, `name`, `class_id`, `email`, `password_hash`) VALUES
('2024BCA001', 'Alan Turing', 1, 'alan@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2024BCA002', 'Ada Lovelace', 1, 'ada@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2023BCA001', 'Grace Hopper', 2, 'grace@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2022BCA001', 'Dennis Ritchie', 3, 'dennis@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2024MCA001', 'Guido van Rossum', 4, 'guido@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2024MCA002', 'Linus Torvalds', 4, 'linus@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2024MCA003', 'Tim Berners-Lee', 4, 'tim@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8'),
('2023MCA001', 'Margaret Hamilton', 5, 'margaret@student.edu', 'scrypt:32768:8:1$uN3vGshZ3Xz9v2QK$89b9d07f3ed63aa4bfbbcd832be041c390a18ddbc7c2dcf6b8f44d1872bca5302f1a6039ea861f681a2eb31853db51ee04bbcefa9c44dddc833446059dbe39f8');

-- Timetable entries for MCA I (Class ID 4) - Monday
INSERT INTO `timetable` (`class_id`, `day`, `hour_number`, `subject_id`, `teacher_id`, `start_time`, `end_time`) VALUES
(4, 'Monday', 1, 7, 4, '09:00 AM', '10:00 AM'),
(4, 'Monday', 2, 8, 2, '10:00 AM', '11:00 AM'),
(4, 'Monday', 3, 7, 4, '11:15 AM', '12:15 PM'),
(4, 'Monday', 4, 8, 2, '01:15 PM', '02:15 PM'),
(4, 'Monday', 5, 7, 4, '02:15 PM', '03:15 PM');
