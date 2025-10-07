-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: MySQL
-- Generated at: 2025-10-07T20:14:20.478Z

CREATE TABLE `auth_users` (
  `id` char(36) PRIMARY KEY,
  `email` varchar(255) UNIQUE COMMENT 'Логін користувача',
  `status` varchar(50) COMMENT 'active, disabled, blocked',
  `created_at` datetime,
  `updated_at` datetime,
  `customer_id` char(36) COMMENT 'Ref: Orders DB (customers.id), без FK',
  `employee_id` char(36) COMMENT 'Ref: Orders DB (employees.id), без FK'
);

CREATE TABLE `auth_credentials` (
  `id` char(36) PRIMARY KEY,
  `user_id` char(36) UNIQUE,
  `password_hash` varchar(255) COMMENT 'hash з сіллю у форматі PHC',
  `algo` varchar(50) COMMENT 'алгоритм хешування',
  `password_updated_at` datetime,
  `updated_at` datetime
);

CREATE TABLE `auth_tokens` (
  `id` char(36) PRIMARY KEY,
  `user_id` char(36),
  `token_hash` varchar(255) COMMENT 'хеш токена доступу',
  `issued_at` datetime,
  `expires_at` datetime,
  `revoked` boolean,
  `last_used_at` datetime,
  `user_agent` varchar(500),
  `ip` varchar(45),
  `scopes` varchar(255) COMMENT 'Опціонально: перелік scope через кому'
);

CREATE TABLE `roles` (
  `id` char(36) PRIMARY KEY,
  `name` varchar(50) UNIQUE COMMENT 'ADMIN, SALES, CUSTOMER, BI_VIEWER',
  `comment` varchar(255)
);

CREATE TABLE `user_roles` (
  `user_id` char(36),
  `role_id` char(36)
);

CREATE INDEX `auth_tokens_index_0` ON `auth_tokens` (`user_id`);

CREATE UNIQUE INDEX `auth_tokens_index_1` ON `auth_tokens` (`token_hash`);

CREATE INDEX `auth_tokens_index_2` ON `auth_tokens` (`expires_at`);

CREATE UNIQUE INDEX `user_roles_index_3` ON `user_roles` (`user_id`, `role_id`);

CREATE INDEX `user_roles_index_4` ON `user_roles` (`role_id`);

ALTER TABLE `auth_credentials` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_users` (`id`);

ALTER TABLE `auth_tokens` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_users` (`id`);

ALTER TABLE `user_roles` ADD FOREIGN KEY (`user_id`) REFERENCES `auth_users` (`id`);

ALTER TABLE `user_roles` ADD FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`);
