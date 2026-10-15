-- College Attendance & Internal Mark Management System
-- MySQL Database Dump & Schema
-- Database Name: college_attendance_db

CREATE DATABASE IF NOT EXISTS `college_attendance_db`;
USE `college_attendance_db`;

-- Drop existing tables if re-importing
DROP TABLE IF EXISTS `attendance_records`;
DROP TABLE IF EXISTS `attendance_reports`;
DROP TABLE IF EXISTS `attendance_sessions`;
DROP TABLE IF EXISTS `timetable`;
DROP TABLE IF EXISTS `students`;
DROP TABLE IF EXISTS `subjects`;
DROP TABLE IF EXISTS `classes`;
DROP TABLE IF EXISTS `teachers`;
DROP TABLE IF EXISTS `admins`;
DROP TABLE IF EXISTS `internal_mark_rules`;

-- Table structure for admins
CREATE TABLE `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100),
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for teachers
CREATE TABLE `teachers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `teacher_id` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `phone` VARCHAR(20),
    `password_hash` VARCHAR(255) NOT NULL,
    `assigned_class_id` INT DEFAULT NULL,
    `assigned_subject_id` INT DEFAULT NULL,
    `role` VARCHAR(20) DEFAULT 'Teacher', -- 'Teacher' or 'Class Tutor'
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for classes
CREATE TABLE `classes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `tutor_id` INT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`tutor_id`) REFERENCES `teachers`(`id`) ON DELETE SET NULL
);

-- Add foreign key back to teachers for assigned_class_id
ALTER TABLE `teachers`
    ADD CONSTRAINT `fk_teachers_assigned_class`
    FOREIGN KEY (`assigned_class_id`) REFERENCES `classes`(`id`) ON DELETE SET NULL;

-- Table structure for subjects
CREATE TABLE `subjects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `class_id` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE
);

-- Add foreign key back to teachers for assigned_subject_id
ALTER TABLE `teachers`
    ADD CONSTRAINT `fk_teachers_assigned_subject`
    FOREIGN KEY (`assigned_subject_id`) REFERENCES `subjects`(`id`) ON DELETE SET NULL;

-- Table structure for students
CREATE TABLE `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `register_number` VARCHAR(50) NOT NULL UNIQUE,
    `department` VARCHAR(100) NOT NULL,
    `class_id` INT NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `phone` VARCHAR(20),
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE
);

-- Table structure for timetable (5 hours per working day)
CREATE TABLE `timetable` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `class_id` INT NOT NULL,
    `day` VARCHAR(20) NOT NULL, -- Monday, Tuesday, Wednesday, Thursday, Friday
    `hour_number` INT NOT NULL, -- 1 to 5
    `subject_id` INT NOT NULL,
    `teacher_id` INT NOT NULL,
    `start_time` VARCHAR(20) DEFAULT '09:30 AM',
    `end_time` VARCHAR(20) DEFAULT '10:30 AM',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_class_day_hour` (`class_id`, `day`, `hour_number`),
    UNIQUE KEY `unique_teacher_day_hour` (`teacher_id`, `day`, `hour_number`)
);

-- Table structure for attendance_sessions
CREATE TABLE `attendance_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `class_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `teacher_id` INT NOT NULL,
    `session_date` DATE NOT NULL,
    `hour_number` INT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Submitted', -- 'Submitted' or 'Cancelled'
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_class_subject_date_hour` (`class_id`, `subject_id`, `session_date`, `hour_number`)
);

-- Table structure for attendance_records
CREATE TABLE `attendance_records` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT NOT NULL,
    `student_id` INT NOT NULL,
    `status` VARCHAR(10) NOT NULL, -- 'Present' or 'Absent'
    FOREIGN KEY (`session_id`) REFERENCES `attendance_sessions`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_session_student` (`session_id`, `student_id`)
);

-- Table structure for attendance_reports
CREATE TABLE `attendance_reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `class_id` INT NOT NULL,
    `subject_id` INT DEFAULT NULL,
    `report_date` DATE NOT NULL,
    `total_students` INT DEFAULT 0,
    `present_count` INT DEFAULT 0,
    `absent_count` INT DEFAULT 0,
    `attendance_percentage` FLOAT DEFAULT 0.0,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON DELETE CASCADE
);

-- Table structure for internal_mark_rules
CREATE TABLE `internal_mark_rules` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `min_percentage` FLOAT NOT NULL,
    `max_percentage` FLOAT NOT NULL,
    `mark` INT NOT NULL,
    `status_label` VARCHAR(50) NOT NULL
);

-- Insert Default Admin (Password: admin123)
-- Hash generated via werkzeug pbkdf2:sha256
INSERT INTO `admins` (`id`, `username`, `password_hash`, `email`) VALUES
(1, 'admin', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 'admin@college.edu');

-- Insert Initial Internal Mark Rules
INSERT INTO `internal_mark_rules` (`id`, `min_percentage`, `max_percentage`, `mark`, `status_label`) VALUES
(1, 90.0, 100.0, 5, 'Eligible'),
(2, 80.0, 89.99, 4, 'Eligible'),
(3, 70.0, 79.99, 3, 'Eligible'),
(4, 60.0, 69.99, 2, 'Eligible'),
(5, 50.0, 59.99, 1, 'Eligible'),
(6, 0.0, 49.99, 0, 'RA – Attendance Below 50%');

-- Insert 5 Classes
INSERT INTO `classes` (`id`, `name`) VALUES
(1, 'BCA I'),
(2, 'BCA II'),
(3, 'BCA III'),
(4, 'MCA I'),
(5, 'MCA II');

-- Insert Teachers / Tutors (Password for all sample teachers: teacher123)
-- Hash for teacher123: scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b
INSERT INTO `teachers` (`id`, `teacher_id`, `name`, `email`, `phone`, `password_hash`, `assigned_class_id`, `role`) VALUES
(1, 'TCH101', 'Dr. Rajesh Kumar', 'rajesh@college.edu', '9876543210', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 4, 'Class Tutor'),
(2, 'TCH102', 'Prof. Sunita Sharma', 'sunita@college.edu', '9876543211', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 5, 'Class Tutor'),
(3, 'TCH103', 'Mr. Anish Verma', 'anish@college.edu', '9876543212', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 1, 'Class Tutor'),
(4, 'TCH104', 'Ms. Priya Nair', 'priya@college.edu', '9876543213', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 2, 'Class Tutor'),
(5, 'TCH105', 'Dr. Suresh Patel', 'suresh@college.edu', '9876543214', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b', 3, 'Class Tutor');

-- Assign Tutors to Classes
UPDATE `classes` SET `tutor_id` = 3 WHERE `id` = 1; -- BCA I -> Anish Verma
UPDATE `classes` SET `tutor_id` = 4 WHERE `id` = 2; -- BCA II -> Priya Nair
UPDATE `classes` SET `tutor_id` = 5 WHERE `id` = 3; -- BCA III -> Suresh Patel
UPDATE `classes` SET `tutor_id` = 1 WHERE `id` = 4; -- MCA I -> Rajesh Kumar
UPDATE `classes` SET `tutor_id` = 2 WHERE `id` = 5; -- MCA II -> Sunita Sharma

-- Insert Subjects for all 5 classes
INSERT INTO `subjects` (`id`, `code`, `name`, `class_id`) VALUES
-- BCA I Subjects
(1, 'BCA101', 'C Programming', 1),
(2, 'BCA102', 'Digital Fundamentals', 1),
(3, 'BCA103', 'Communication Skills', 1),
-- BCA II Subjects
(4, 'BCA201', 'Data Structures in C++', 2),
(5, 'BCA202', 'Java Programming', 2),
(6, 'BCA203', 'Operating Systems', 2),
-- BCA III Subjects
(7, 'BCA301', 'Python Programming', 3),
(8, 'BCA302', 'Software Engineering', 3),
(9, 'BCA303', 'Computer Networks', 3),
-- MCA I Subjects
(10, 'MCA101', 'Advanced Data Structures', 4),
(11, 'MCA102', 'Python Programming', 4),
(12, 'MCA103', 'Database Management Systems', 4),
(13, 'MCA104', 'Computer Networks', 4),
-- MCA II Subjects
(14, 'MCA201', 'Cloud Computing', 5),
(15, 'MCA202', 'Machine Learning', 5),
(16, 'MCA203', 'Web Technologies', 5);

-- Update Teacher Assigned Subjects
UPDATE `teachers` SET `assigned_subject_id` = 10 WHERE `id` = 1; -- Rajesh -> MCA101
UPDATE `teachers` SET `assigned_subject_id` = 14 WHERE `id` = 2; -- Sunita -> MCA201
UPDATE `teachers` SET `assigned_subject_id` = 1 WHERE `id` = 3;  -- Anish -> BCA101
UPDATE `teachers` SET `assigned_subject_id` = 4 WHERE `id` = 4;  -- Priya -> BCA201
UPDATE `teachers` SET `assigned_subject_id` = 7 WHERE `id` = 5;  -- Suresh -> BCA301

-- Insert Students for each class (Password: student123)
-- Hash for student123: scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b
INSERT INTO `students` (`id`, `name`, `register_number`, `department`, `class_id`, `email`, `phone`, `password_hash`) VALUES
-- BCA I Students
(1, 'Aravind Swamy', '23BCA01', 'Computer Applications', 1, 'aravind@college.edu', '9123456780', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(2, 'Bhavana Devi', '23BCA02', 'Computer Applications', 1, 'bhavana@college.edu', '9123456781', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(3, 'Chiranjeevi R', '23BCA03', 'Computer Applications', 1, 'chiru@college.edu', '9123456782', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),

-- BCA II Students
(4, 'Deepak Kumar', '22BCA01', 'Computer Applications', 2, 'deepak@college.edu', '9123456783', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(5, 'Divya Prakash', '22BCA02', 'Computer Applications', 2, 'divya@college.edu', '9123456784', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),

-- BCA III Students
(6, 'Gokulnath M', '21BCA01', 'Computer Applications', 3, 'gokul@college.edu', '9123456785', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(7, 'Hariharan S', '21BCA02', 'Computer Applications', 3, 'hari@college.edu', '9123456786', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),

-- MCA I Students
(8, 'Kavitha Ramesh', '23MCA01', 'Computer Applications', 4, 'kavitha@college.edu', '9123456787', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(9, 'Karthik Raja', '23MCA02', 'Computer Applications', 4, 'karthik@college.edu', '9123456788', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(10, 'Lavanya S', '23MCA03', 'Computer Applications', 4, 'lavanya@college.edu', '9123456789', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(11, 'Manoj Kumar', '23MCA04', 'Computer Applications', 4, 'manoj@college.edu', '9123456790', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),

-- MCA II Students
(12, 'Naveen Prashanth', '22MCA01', 'Computer Applications', 5, 'naveen@college.edu', '9123456791', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b'),
(13, 'Nivedita S', '22MCA02', 'Computer Applications', 5, 'nivedita@college.edu', '9123456792', 'scrypt:32768:8:1$u7iP8lHw8N9e1f2g$f5485459312d8a571754024c084045f284e3661be491ebfefd7eb78550cb51b2e1bf3a5f9cb463c299bd51aeb16d1f057eecfc6e7e0e7d97607a3c3df5b4e70b');

-- Timetable Entries (5 hours per working day for MCA I as sample)
INSERT INTO `timetable` (`class_id`, `day`, `hour_number`, `subject_id`, `teacher_id`, `start_time`, `end_time`) VALUES
-- MCA I Timetable - Monday
(4, 'Monday', 1, 10, 1, '09:30 AM', '10:30 AM'),
(4, 'Monday', 2, 11, 1, '10:30 AM', '11:30 AM'),
(4, 'Monday', 3, 12, 1, '11:30 AM', '12:30 PM'),
(4, 'Monday', 4, 13, 1, '01:30 PM', '02:30 PM'),
(4, 'Monday', 5, 10, 1, '02:30 PM', '03:30 PM'),

-- MCA II Timetable - Monday
(5, 'Monday', 1, 14, 2, '09:30 AM', '10:30 AM'),
(5, 'Monday', 2, 15, 2, '10:30 AM', '11:30 AM'),
(5, 'Monday', 3, 16, 2, '11:30 AM', '12:30 PM'),

-- BCA I Timetable - Monday
(1, 'Monday', 1, 1, 3, '09:30 AM', '10:30 AM'),
(1, 'Monday', 2, 2, 3, '10:30 AM', '11:30 AM'),
(1, 'Monday', 3, 3, 3, '11:30 AM', '12:30 PM'),

-- BCA II Timetable - Monday
(2, 'Monday', 1, 4, 4, '09:30 AM', '10:30 AM'),
(2, 'Monday', 2, 5, 4, '10:30 AM', '11:30 AM'),

-- BCA III Timetable - Monday
(3, 'Monday', 1, 7, 5, '09:30 AM', '10:30 AM'),
(3, 'Monday', 2, 8, 5, '10:30 AM', '11:30 AM');

-- Sample Attendance Sessions
INSERT INTO `attendance_sessions` (`id`, `class_id`, `subject_id`, `teacher_id`, `session_date`, `hour_number`, `status`) VALUES
(1, 4, 10, 1, '2025-02-10', 1, 'Submitted'),
(2, 4, 10, 1, '2025-02-11', 1, 'Submitted'),
(3, 4, 10, 1, '2025-02-12', 1, 'Submitted'),
(4, 4, 10, 1, '2025-02-13', 1, 'Submitted'),
(5, 4, 10, 1, '2025-02-14', 1, 'Submitted');

-- Sample Attendance Records for MCA I Students (IDs 8, 9, 10, 11)
-- Kavitha (8): 5/5 Present (100% -> Mark 5, Eligible)
-- Karthik (9): 4/5 Present (80% -> Mark 4, Eligible)
-- Lavanya (10): 3/5 Present (60% -> Mark 2, Eligible)
-- Manoj (11): 2/5 Present (40% -> Mark 0, RA – Attendance Below 50%)

INSERT INTO `attendance_records` (`session_id`, `student_id`, `status`) VALUES
-- Session 1
(1, 8, 'Present'), (1, 9, 'Present'), (1, 10, 'Present'), (1, 11, 'Absent'),
-- Session 2
(2, 8, 'Present'), (2, 9, 'Present'), (2, 10, 'Present'), (2, 11, 'Present'),
-- Session 3
(3, 8, 'Present'), (3, 9, 'Present'), (3, 10, 'Absent'), (3, 11, 'Absent'),
-- Session 4
(4, 8, 'Present'), (4, 9, 'Present'), (4, 10, 'Present'), (4, 11, 'Absent'),
-- Session 5
(5, 8, 'Present'), (5, 9, 'Absent'),  (5, 10, 'Absent'),  (5, 11, 'Present');
