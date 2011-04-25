-- phpMyAdmin SQL Dump
-- version 3.3.10
-- http://www.phpmyadmin.net
--
-- Host: mysql.tf2mv.com
-- Generation Time: Apr 25, 2011 at 04:29 PM
-- Server version: 5.1.53
-- PHP Version: 5.2.15

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `tf2mv`
--

-- --------------------------------------------------------

--
-- Table structure for table `item_found`
--

CREATE TABLE IF NOT EXISTS `item_found` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ip` int(10) unsigned NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `steamid` varchar(32) NOT NULL,
  `method` tinyint(4) NOT NULL,
  `quality` tinyint(4) NOT NULL,
  `item` varchar(40) NOT NULL,
  `propername` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_2` (`ip`,`timestamp`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=35 ;

-- --------------------------------------------------------

--
-- Table structure for table `trades`
--

CREATE TABLE IF NOT EXISTS `trades` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `steamid1` varchar(32) NOT NULL,
  `steamid2` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `timestamp` (`timestamp`,`steamid1`,`steamid2`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `trade_items`
--

CREATE TABLE IF NOT EXISTS `trade_items` (
  `trade` bigint(20) NOT NULL,
  `item` bigint(20) NOT NULL,
  PRIMARY KEY (`trade`,`item`),
  KEY `item` (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `trade_items`
--
ALTER TABLE `trade_items`
  ADD CONSTRAINT `trade_items_ibfk_2` FOREIGN KEY (`item`) REFERENCES `item_found` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `trade_items_ibfk_1` FOREIGN KEY (`trade`) REFERENCES `trades` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
