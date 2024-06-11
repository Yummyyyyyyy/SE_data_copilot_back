/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80027 (8.0.27)
 Source Host           : localhost:3306
 Source Schema         : takeaway

 Target Server Type    : MySQL
 Target Server Version : 80027 (8.0.27)
 File Encoding         : 65001

 Date: 11/06/2024 12:59:41
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app01_item
-- ----------------------------
DROP TABLE IF EXISTS `app01_item`;
CREATE TABLE `app01_item` (
  `index` int DEFAULT NULL,
  `Item_id` varchar(32) NOT NULL,
  `Item_name` varchar(64) DEFAULT NULL,
  `Item_type` varchar(32) DEFAULT NULL,
  `Item_price` int DEFAULT NULL,
  PRIMARY KEY (`Item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of app01_item
-- ----------------------------
BEGIN;
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (1, 'I01', '汉堡', '快餐', 12);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (2, 'I02', '薯条', '快餐', 10);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (3, 'I03', '可乐', '饮料', 5);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (4, 'I04', '扬州炒饭', '中餐', 13);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (5, 'I05', '蛋炒饭', '中餐', 10);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (6, 'I06', '里脊肉炒面', '中餐', 12);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (7, 'I07', '新疆炒米粉', '中餐', 15);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (8, 'I08', '番茄炒鸡蛋', '中餐', 10);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (9, 'I09', '糖醋小酥肉', '中餐', 15);
INSERT INTO `app01_item` (`index`, `Item_id`, `Item_name`, `Item_type`, `Item_price`) VALUES (10, 'I10', '炒青菜', '中餐', 10);
COMMIT;

-- ----------------------------
-- Table structure for app01_order
-- ----------------------------
DROP TABLE IF EXISTS `app01_order`;
CREATE TABLE `app01_order` (
  `index` int DEFAULT NULL,
  `Order_id` varchar(32) NOT NULL,
  `Customer_id` varchar(32) DEFAULT NULL,
  `Store_id` varchar(32) DEFAULT NULL,
  `Item_id` varchar(32) DEFAULT NULL,
  `Rider_id` varchar(32) DEFAULT NULL,
  `Order_time` datetime DEFAULT NULL,
  `Order_price` int DEFAULT NULL,
  PRIMARY KEY (`Order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of app01_order
-- ----------------------------
BEGIN;
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (1, 'A01', 'C01', 'S01', 'I01', 'R01', '2023-05-12 00:00:00', 12);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (2, 'A02', 'C02', 'S02', 'I02', 'R02', '2023-05-12 00:00:00', 10);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (3, 'A03', 'C03', 'S03', 'I03', 'R03', '2023-05-14 00:00:00', 5);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (4, 'A04', 'C04', 'S04', 'I04', 'R04', '2023-05-15 00:00:00', 13);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (5, 'A05', 'C01', 'S04', 'I01', 'R05', '2023-05-17 00:00:00', 12);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (6, 'A06', 'C02', 'S01', 'I02', 'R01', '2023-05-17 00:00:00', 10);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (7, 'A07', 'C03', 'S02', 'I03', 'R03', '2023-05-18 00:00:00', 5);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (8, 'A08', 'C04', 'S03', 'I04', 'R05', '2023-05-20 00:00:00', 13);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (9, 'A09', 'C05', 'S04', 'I05', 'R02', '2023-05-20 00:00:00', 10);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (10, 'A10', 'C06', 'S01', 'I06', 'R04', '2023-05-21 00:00:00', 12);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (11, 'A11', 'C07', 'S02', 'I07', 'R06', '2023-05-22 00:00:00', 15);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (12, 'A12', 'C08', 'S03', 'I08', 'R01', '2023-05-22 00:00:00', 10);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (13, 'A13', 'C09', 'S04', 'I09', 'R02', '2023-05-22 00:00:00', 15);
INSERT INTO `app01_order` (`index`, `Order_id`, `Customer_id`, `Store_id`, `Item_id`, `Rider_id`, `Order_time`, `Order_price`) VALUES (14, 'A14', 'C10', 'S01', 'I10', 'R03', '2023-05-24 00:00:00', 10);
COMMIT;

-- ----------------------------
-- Table structure for app01_store
-- ----------------------------
DROP TABLE IF EXISTS `app01_store`;
CREATE TABLE `app01_store` (
  `index` int DEFAULT NULL,
  `Store_id` varchar(32) NOT NULL,
  `Store_name` varchar(64) DEFAULT NULL,
  `Store_area` varchar(32) DEFAULT NULL,
  `Store_address` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`Store_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of app01_store
-- ----------------------------
BEGIN;
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
