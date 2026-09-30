-- College Admission Seat Allocation System (MCA Project)
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `college_admission`;
USE `college_admission`;

-- Table structure for seat reservation settings
CREATE TABLE IF NOT EXISTS `settings` (
    `id` INT PRIMARY KEY DEFAULT 1,
    `oc_seats` INT NOT NULL DEFAULT 9,
    `bc_seats` INT NOT NULL DEFAULT 8,
    `bcm_seats` INT NOT NULL DEFAULT 1,
    `mbc_seats` INT NOT NULL DEFAULT 6,
    `sc_seats` INT NOT NULL DEFAULT 5,
    `sca_seats` INT NOT NULL DEFAULT 1,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default seat reservation settings (Total 30 Seats)
INSERT INTO `settings` (`id`, `oc_seats`, `bc_seats`, `bcm_seats`, `mbc_seats`, `sc_seats`, `sca_seats`)
VALUES (1, 9, 8, 1, 6, 5, 1)
ON DUPLICATE KEY UPDATE
`oc_seats` = VALUES(`oc_seats`),
`bc_seats` = VALUES(`bc_seats`),
`bcm_seats` = VALUES(`bcm_seats`),
`mbc_seats` = VALUES(`mbc_seats`),
`sc_seats` = VALUES(`sc_seats`),
`sca_seats` = VALUES(`sca_seats`);

-- Table structure for students (NO quota column)
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `application_no` VARCHAR(50) UNIQUE NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `gender` VARCHAR(20) NOT NULL,
    `community` VARCHAR(20) NOT NULL,
    `marks` FLOAT NOT NULL,
    `rank_no` INT NOT NULL,
    `admission_date` DATE DEFAULT NULL,
    `status` VARCHAR(20) DEFAULT 'Waiting',
    `allocated_category` VARCHAR(20) DEFAULT NULL,
    `remark` TEXT DEFAULT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);
