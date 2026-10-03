-- Business Supplier & Purchase Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `supplier_purchase_db`;
USE `supplier_purchase_db`;

-- Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for suppliers
CREATE TABLE IF NOT EXISTS `suppliers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `supplier_name` VARCHAR(100) NOT NULL,
    `company_name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `address` TEXT,
    `status` VARCHAR(20) DEFAULT 'Active', -- Active, Inactive
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for products
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_name` VARCHAR(100) NOT NULL,
    `product_code` VARCHAR(50) UNIQUE NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `purchase_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `current_stock` INT NOT NULL DEFAULT 0,
    `min_stock_level` INT NOT NULL DEFAULT 5,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table structure for purchases
CREATE TABLE IF NOT EXISTS `purchases` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `purchase_number` VARCHAR(50) UNIQUE NOT NULL,
    `supplier_id` INT NOT NULL,
    `purchase_date` DATE NOT NULL,
    `status` VARCHAR(20) DEFAULT 'Pending', -- Pending, Ordered, Received, Cancelled
    `total_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `notes` TEXT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`id`) ON DELETE CASCADE
);

-- Table structure for purchase_items
CREATE TABLE IF NOT EXISTS `purchase_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `purchase_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `purchase_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `subtotal` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (`purchase_id`) REFERENCES `purchases`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE
);

-- Seed Initial Admin User (Username: admin, Password: admin123)
-- Password hash generated using werkzeug pbkdf2:sha256
INSERT INTO `admins` (`username`, `password_hash`) VALUES
('admin', 'scrypt:32768:8:1$Kq3Kq2Gq$c8cf869a83a005ee5334eb2bc3515ca4f10a8275553dcfb25a38a7bd8cdd9b7036e4f3a76efdd4237bb957b8c73ee8555e6ffc6ed4646a782b1c676fef78ea6a')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Initial Suppliers
INSERT INTO `suppliers` (`id`, `supplier_name`, `company_name`, `phone`, `email`, `address`, `status`) VALUES
(1, 'Rajesh Sharma', 'Apex Global Traders', '+91 9876543210', 'rajesh@apexglobal.com', '123 Commercial Hub, MG Road, Mumbai', 'Active'),
(2, 'Priya Verma', 'Tech & Tools Supplies', '+91 9812345678', 'priya@techtools.com', '45 Industrial Estate, Electronic City, Bengaluru', 'Active'),
(3, 'Suresh Kumar', 'Prime Logistics & Goods', '+91 9765432109', 'suresh@primelogistics.com', '78 Warehouse Zone, GT Road, Delhi', 'Inactive')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Initial Products
INSERT INTO `products` (`id`, `product_name`, `product_code`, `category`, `purchase_price`, `current_stock`, `min_stock_level`) VALUES
(1, 'Ergonomic Office Chair', 'PROD-101', 'Furniture', 3500.00, 15, 5),
(2, 'Wireless Mechanical Keyboard', 'PROD-102', 'Electronics', 2200.00, 3, 10),
(3, 'LED Desktop Monitor 24"', 'PROD-103', 'Electronics', 8500.00, 0, 4),
(4, 'Heavy Duty Storage Shelves', 'PROD-104', 'Equipment', 4500.00, 25, 8)
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Initial Purchases
INSERT INTO `purchases` (`id`, `purchase_number`, `supplier_id`, `purchase_date`, `status`, `total_amount`, `notes`) VALUES
(1, 'PUR-1001', 1, '2023-10-10', 'Received', 17500.00, 'Initial stock purchase for office chairs'),
(2, 'PUR-1002', 2, '2023-10-15', 'Pending', 11000.00, 'Awaiting approval for keyboards'),
(3, 'PUR-1003', 1, '2023-10-18', 'Ordered', 34000.00, 'Monitors batch order placed with Apex Global')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed Initial Purchase Items
INSERT INTO `purchase_items` (`id`, `purchase_id`, `product_id`, `quantity`, `purchase_price`, `subtotal`) VALUES
(1, 1, 1, 5, 3500.00, 17500.00),
(2, 2, 2, 5, 2200.00, 11000.00),
(3, 3, 3, 4, 8500.00, 34000.00)
ON DUPLICATE KEY UPDATE `id`=`id`;
