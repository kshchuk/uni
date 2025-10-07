-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: MySQL
-- Generated at: 2025-10-07T20:14:24.009Z

CREATE TABLE `payments` (
  `id` char(36) PRIMARY KEY,
  `order_id` char(36) COMMENT 'Ref: Orders DB (orders.id), без FK між БД',
  `method` varchar(50) COMMENT 'card, paypal, etc.',
  `paid_at` datetime,
  `amount` decimal(10,2)
);

CREATE INDEX `payments_index_0` ON `payments` (`order_id`);
