-- Laboratory Stock Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `laboratory_stock`;
USE `laboratory_stock`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for items
CREATE TABLE IF NOT EXISTS `items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `item_name` VARCHAR(100) NOT NULL,
    `item_code` VARCHAR(50) UNIQUE NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `quantity` INT NOT NULL DEFAULT 0,
    `minimum_stock` INT NOT NULL DEFAULT 5,
    `unit` VARCHAR(20) NOT NULL DEFAULT 'Pcs',
    `location` VARCHAR(100) NOT NULL DEFAULT 'Main Lab',
    `added_date` DATE NOT NULL
);

-- Table structure for stock_history
CREATE TABLE IF NOT EXISTS `stock_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `item_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `transaction_type` VARCHAR(50) NOT NULL, -- 'Stock Added', 'Stock Used'
    `date` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `remarks` VARCHAR(255),
    FOREIGN KEY (`item_id`) REFERENCES `items`(`id`) ON DELETE CASCADE
);

-- Seed default admin account (username: admin, password: admin123)
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$GRLCTy83KgPW3O5N$31dc342c343140bef8e32ec4cf25b7d037c28d5e599c35d4273dd77c9907aa8d25ee979258c40628e1ee09e9cc4e16016c289adcda385d931e7f56fb1f66e040');

-- Seed initial laboratory stock items
INSERT INTO `items` (`item_name`, `item_code`, `category`, `quantity`, `minimum_stock`, `unit`, `location`, `added_date`) VALUES
('Desktop PC i5 12th Gen', 'COMP-001', 'Computer Equipment', 25, 5, 'Units', 'Lab 1 - Rack A', CURDATE()),
('Optical Mouse USB', 'COMP-002', 'Computer Equipment', 40, 10, 'Pcs', 'Lab 1 - Shelf B', CURDATE()),
('Arduino Uno R3', 'ELEC-001', 'Electronic Components', 15, 5, 'Pcs', 'Electronics Lab - Cabinet 1', CURDATE()),
('Resistor Kit (10k Ohm)', 'ELEC-002', 'Electronic Components', 3, 10, 'Packs', 'Electronics Lab - Drawer 3', CURDATE()),
('Digital Multimeter', 'LAB-001', 'Laboratory Equipment', 8, 2, 'Units', 'Testing Bay 2', CURDATE()),
('Oscilloscope 50MHz', 'LAB-002', 'Laboratory Equipment', 0, 2, 'Units', 'Testing Bay 1', CURDATE()),
('A4 Printing Paper', 'STAT-001', 'Stationery', 50, 10, 'Reams', 'Store Room - Shelf A', CURDATE()),
('Whiteboard Markers', 'STAT-002', 'Stationery', 2, 5, 'Boxes', 'Store Room - Shelf B', CURDATE());

-- Seed initial stock history entries
INSERT INTO `stock_history` (`item_id`, `quantity`, `transaction_type`, `remarks`) VALUES
(1, 25, 'Stock Added', 'Initial inventory setup'),
(2, 40, 'Stock Added', 'Initial inventory setup'),
(3, 15, 'Stock Added', 'Initial inventory setup'),
(4, 3, 'Stock Added', 'Initial inventory setup'),
(5, 8, 'Stock Added', 'Initial inventory setup'),
(6, 0, 'Stock Added', 'Item registered, stock zero'),
(7, 50, 'Stock Added', 'Initial inventory setup'),
(8, 2, 'Stock Added', 'Initial inventory setup');
