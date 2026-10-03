-- College Lab Consumables Inventory System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `lab_consumables_db`;
USE `lab_consumables_db`;

-- Table 1: admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL
);

-- Table 2: consumables
CREATE TABLE IF NOT EXISTS `consumables` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `consumable_name` VARCHAR(100) NOT NULL,
    `item_code` VARCHAR(50) NOT NULL UNIQUE,
    `category` VARCHAR(50) NOT NULL,
    `quantity` INT NOT NULL DEFAULT 0,
    `minimum_stock` INT NOT NULL DEFAULT 0,
    `unit` VARCHAR(20) NOT NULL,
    `lab_name` VARCHAR(100) NOT NULL,
    `added_date` DATE NOT NULL
);

-- Table 3: stock_history
CREATE TABLE IF NOT EXISTS `stock_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `consumable_id` INT NOT NULL,
    `transaction_type` VARCHAR(20) NOT NULL,
    `quantity` INT NOT NULL,
    `transaction_date` DATE NOT NULL,
    `remarks` VARCHAR(255),
    FOREIGN KEY (`consumable_id`) REFERENCES `consumables`(`id`) ON DELETE CASCADE
);

-- Default Admin Seed (Username: admin, Password: admin123 hashed via Werkzeug)
-- Password hash below corresponds to 'admin123'
INSERT INTO `admins` (`username`, `password`)
VALUES ('admin', 'scrypt:32768:8:1$u7xH2q9Y$5e3c7f99a5e88801d9f5832a8848d7c9a7eddfd482488812a64c4c16dd0a51e604471923e6b72a6a3e6f991fdf24385966cf1d29323730e7048701e6a695e2df')
ON DUPLICATE KEY UPDATE `username`=`username`;

-- Seed Sample Consumables
INSERT INTO `consumables` (`consumable_name`, `item_code`, `category`, `quantity`, `minimum_stock`, `unit`, `lab_name`, `added_date`) VALUES
('Sodium Hydroxide Pellets', 'CHEM-101', 'Chemicals', 25, 10, 'Kg', 'Chemistry Lab', '2025-01-10'),
('Glass Beaker 250ml', 'GLAS-201', 'Glassware', 3, 10, 'Pieces', 'Chemistry Lab', '2025-01-12'),
('A4 Printing Paper', 'STAT-301', 'Stationery', 0, 5, 'Reams', 'Computer Lab 1', '2025-01-15'),
('Resistor Pack 10k Ohm', 'ELEC-401', 'Electronic Components', 100, 25, 'Packs', 'Electronics Lab', '2025-01-18'),
('Ethanol 99% Pure', 'CHEM-102', 'Chemicals', 4, 5, 'Bottles', 'Chemistry Lab', '2025-01-20'),
('Microfiber Cloth', 'CLEN-501', 'Cleaning Materials', 15, 5, 'Packs', 'Hardware Lab', '2025-01-22')
ON DUPLICATE KEY UPDATE `item_code`=`item_code`;

-- Seed Sample Stock History
INSERT INTO `stock_history` (`consumable_id`, `transaction_type`, `quantity`, `transaction_date`, `remarks`) VALUES
(1, 'Stock Added', 25, '2025-01-10', 'Initial stock purchase'),
(2, 'Stock Added', 15, '2025-01-12', 'Initial stock purchase'),
(2, 'Stock Used', 12, '2025-01-14', 'Used in Organic Chemistry experiment'),
(3, 'Stock Added', 10, '2025-01-15', 'Monthly supply'),
(3, 'Stock Used', 10, '2025-01-25', 'Exam paper printing'),
(4, 'Stock Added', 100, '2025-01-18', 'Bulk purchase for lab practicals');
