-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: MySQL
-- Generated at: 2025-10-07T20:14:22.899Z

CREATE TABLE `customers` (
  `id` char(36) PRIMARY KEY,
  `first_name` varchar(100),
  `last_name` varchar(100),
  `email` varchar(255) UNIQUE,
  `phone` varchar(50),
  `created_at` datetime,
  `updated_at` datetime
);

CREATE TABLE `regions` (
  `id` char(36) PRIMARY KEY,
  `name` varchar(100),
  `code` varchar(10) UNIQUE COMMENT 'Код регіону'
);

CREATE TABLE `employees` (
  `id` char(36) PRIMARY KEY,
  `first_name` varchar(100),
  `last_name` varchar(100),
  `email` varchar(255) UNIQUE,
  `hired_at` date,
  `is_manager` boolean COMMENT 'Флаг керівника',
  `region_id` char(36) COMMENT 'Регіон відповідальності'
);

CREATE TABLE `orders` (
  `id` char(36) PRIMARY KEY,
  `customer_id` char(36),
  `employee_id` char(36),
  `region_id` char(36),
  `order_date` datetime,
  `status` varchar(20) COMMENT 'new, paid, shipped, cancelled',
  `total_amount` decimal(10,2),
  `created_at` datetime,
  `updated_at` datetime
);

CREATE TABLE `order_items` (
  `id` char(36) PRIMARY KEY,
  `order_id` char(36),
  `product_id` char(36) COMMENT 'Ref: Catalog DB (products.id), без FK між БД',
  `quantity` integer,
  `unit_price` decimal(10,2),
  `discount` decimal(10,2) COMMENT 'Знижка на позицію (грошима або часткою)'
);

CREATE INDEX `order_customer_idx` ON `orders` (`customer_id`);

CREATE INDEX `order_employee_idx` ON `orders` (`employee_id`);

CREATE INDEX `order_region_idx` ON `orders` (`region_id`);

CREATE INDEX `order_date_idx` ON `orders` (`order_date`);

CREATE INDEX `oi_order_idx` ON `order_items` (`order_id`);

CREATE INDEX `oi_product_idx` ON `order_items` (`product_id`);

ALTER TABLE `employees` ADD FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`);

ALTER TABLE `orders` ADD FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`);

ALTER TABLE `orders` ADD FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`);

ALTER TABLE `orders` ADD FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`);

ALTER TABLE `order_items` ADD FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`);
