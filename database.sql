-- College Placement & Job Application Portal
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `placement_portal_db`;
USE `placement_portal_db`;

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

-- Table structure for job opportunities
CREATE TABLE IF NOT EXISTS `jobs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_name` VARCHAR(100) NOT NULL,
    `job_role` VARCHAR(100) NOT NULL,
    `salary_package` VARCHAR(50) NOT NULL,
    `eligibility_criteria` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for job applications
CREATE TABLE IF NOT EXISTS `applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `job_id` INT NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Selected, Rejected
    `applied_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE
);

-- Seed initial job opportunities
INSERT INTO `jobs` (`company_name`, `job_role`, `salary_package`, `eligibility_criteria`, `description`) VALUES
('TechSolutions Inc.', 'Software Engineer Trainee', '6.5 LPA', 'BE/B.Tech/MCA/M.Sc (CS/IT), 60% throughout', 'Looking for enthusiastic entry-level software developers with strong problem-solving and coding skills in Python, Java, or C++.'),
('DataDynamics Ltd.', 'Data Analyst', '5.0 LPA', 'All B.E/B.Tech, MCA, B.Sc (Maths/Stats/CS)', 'Responsible for analyzing datasets, building interactive dashboards, and preparing data insights for clients.'),
('CloudScale Systems', 'DevOps & Cloud Associate', '7.2 LPA', 'CSE, IT, ECE, MCA - 65% aggregate', 'Role involves working with AWS/Azure services, Docker containerization, CI/CD pipelines, and Linux administration.'),
('NextGen Solutions', 'UI/UX Frontend Developer', '4.8 LPA', 'Open to all departments with Web Development skills', 'Front-end development using HTML5, CSS3, JavaScript, and Bootstrap/React framework.'),
('FinTech Corp', 'QA & Automation Engineer', '5.5 LPA', 'CSE, IT, ECE, MCA', 'Software testing role including automated test scripts execution, bug tracking, and quality assurance.');
