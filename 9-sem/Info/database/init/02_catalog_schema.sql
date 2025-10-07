-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: MySQL
-- Generated at: 2025-10-07T20:14:21.727Z

CREATE TABLE `categories` (
  `id` char(36) PRIMARY KEY,
  `name` varchar(255),
  `parent_category_id` char(36) COMMENT 'Nullable; ієрархія категорій'
);

CREATE TABLE `products` (
  `id` char(36) PRIMARY KEY,
  `name` varchar(255),
  `sku` varchar(100) UNIQUE COMMENT 'Артикул',
  `category_id` char(36),
  `price` decimal(10,2) COMMENT 'Ціна продажу',
  `cost` decimal(10,2) COMMENT 'Собівартість',
  `status` varchar(20) COMMENT 'active/inactive',
  `created_at` datetime,
  `updated_at` datetime
);

CREATE UNIQUE INDEX `categories_index_0` ON `categories` (`name`);

CREATE INDEX `products_index_1` ON `products` (`category_id`);

ALTER TABLE `categories` ADD FOREIGN KEY (`parent_category_id`) REFERENCES `categories` (`id`);

ALTER TABLE `products` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);
