-- Small Business Sales & Customer Management System
-- Database Schema for MySQL / XAMPP phpMyAdmin

CREATE DATABASE IF NOT EXISTS `service_booking_db`;
USE `service_booking_db`;

-- 1. Table structure for admins
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `name` VARCHAR(100) NOT NULL DEFAULT 'Administrator',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table structure for customers
CREATE TABLE IF NOT EXISTS `customers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `address` TEXT NOT NULL,
    `customer_type` VARCHAR(20) NOT NULL DEFAULT 'New', -- New, Regular, VIP
    `registration_date` DATE NOT NULL
);

-- 3. Table structure for products
CREATE TABLE IF NOT EXISTS `products` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `product_code` VARCHAR(50) UNIQUE NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `selling_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `available_stock` INT NOT NULL DEFAULT 0,
    `min_stock_level` INT NOT NULL DEFAULT 5,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table structure for sales
CREATE TABLE IF NOT EXISTS `sales` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sale_number` VARCHAR(50) UNIQUE NOT NULL,
    `customer_id` INT NOT NULL,
    `sale_date` DATE NOT NULL,
    `total_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `discount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `grand_total` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `payment_status` VARCHAR(20) NOT NULL DEFAULT 'Paid', -- Paid, Partially Paid, Unpaid
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`customer_id`) REFERENCES `customers`(`id`) ON DELETE CASCADE
);

-- 5. Table structure for sale_items
CREATE TABLE IF NOT EXISTS `sale_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `sale_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL DEFAULT 1,
    `unit_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `total_price` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (`sale_id`) REFERENCES `sales`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE RESTRICT
);

-- Seed initial admin user (username: admin, password: password123 / admin123 hash)
-- Note: The application also supports password hashing dynamically.
INSERT INTO `admins` (`id`, `username`, `password_hash`, `name`) VALUES
(1, 'admin', 'scrypt:32768:8:1$vOa1sU4K6h5y0G1j$9e9a11ef126581b2bfb217036d0e828e18df063e527f5fa8c21a4fa89bd78a2e1d7cf9d91fbb2f86aa59ca54839ee8cb57dbb69b59740520fbfeeb6c2d15915a', 'System Administrator')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed default products
INSERT INTO `products` (`id`, `name`, `product_code`, `category`, `selling_price`, `available_stock`, `min_stock_level`) VALUES
(1, 'Wireless Ergonomic Mouse', 'PRD-1001', 'Electronics', 799.00, 25, 5),
(2, 'Mechanical RGB Keyboard', 'PRD-1002', 'Electronics', 2499.00, 12, 3),
(3, 'USB-C Fast Charger 65W', 'PRD-1003', 'Accessories', 1299.00, 4, 5),
(4, 'Noise Cancelling Headphones', 'PRD-1004', 'Audio', 3999.00, 0, 2),
(5, 'Stainless Steel Water Bottle', 'PRD-1005', 'Home & Office', 499.00, 30, 8)
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Seed default customers
INSERT INTO `customers` (`id`, `name`, `phone`, `email`, `address`, `customer_type`, `registration_date`) VALUES
(1, 'Rahul Sharma', '9876543210', 'rahul@example.com', '123 Main Street, City', 'Regular', CURDATE()),
(2, 'Priya Patel', '9812345678', 'priya@example.com', '45 Park View, City', 'VIP', CURDATE()),
(3, 'Ankit Kumar', '9765432109', 'ankit@example.com', '78 Market Road, City', 'New', CURDATE())
ON DUPLICATE KEY UPDATE `id`=`id`;
