-- College Digital Document Verification System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `doc_verification_db`;
USE `doc_verification_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

-- Table structure for documents
CREATE TABLE IF NOT EXISTS `documents` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `document_name` VARCHAR(150) NOT NULL,
    `document_type` VARCHAR(50) NOT NULL, -- ID Proof, Mark Sheet, Bonafide Certificate, Transfer Certificate, Other
    `filename` VARCHAR(255) NOT NULL,
    `file_path` VARCHAR(255) NOT NULL,
    `upload_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Verified, Rejected
    `admin_remark` TEXT DEFAULT NULL,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE
);

-- Seed default administrator credentials
-- Default Admin Username: admin
-- Default Admin Password: admin123 (werkzeug pbkdf2:sha256 hash below)
INSERT INTO `admins` (`username`, `password_hash`)
VALUES ('admin', 'scrypt:32768:8:1$u7xK382x9v4I0fX2$8f9e6d0a7a00f215d8f6d729bc6f621325ed8a1789b53fa417b1897d26bbdf608eef1db84e9ffef3a31c19b0d2382c40c6c747f48bbfb2f9024f2b1c4bdc63b7')
ON DUPLICATE KEY UPDATE `id`=`id`;

/*
====================================================================
XAMPP & PHPMYADMIN SETUP INSTRUCTIONS
====================================================================
1. Open XAMPP Control Panel and start Apache and MySQL services.
2. Open your browser and go to http://localhost/phpmyadmin/
3. Click on the "SQL" tab at the top.
4. Copy and paste the contents of this file (database.sql) into the SQL editor.
5. Click "Go" to execute and create the `doc_verification_db` database and tables.

====================================================================
VS CODE RUN STEPS
====================================================================
1. Open the project folder `college_document_verification` in VS Code.
2. Open terminal in VS Code (Ctrl + ` or Terminal > New Terminal).
3. Install dependencies:
   pip install -r requirements.txt
4. Run the Flask Application:
   python app.py
5. Open browser at http://127.0.0.1:5000/

Default Admin Credentials:
Username: admin
Password: admin123
====================================================================
*/
