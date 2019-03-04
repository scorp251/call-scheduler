DROP TABLE IF EXISTS `scheduled_calls`;
CREATE TABLE `scheduled_calls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year` int(11) DEFAULT NULL,
  `month` varchar(45) DEFAULT NULL,
  `nmonth` int(11) DEFAULT NULL,
  `day` int(11) DEFAULT NULL,
  `hours` int(11) DEFAULT NULL,
  `minutes` int(11) DEFAULT NULL,
  `fname` varchar(45) DEFAULT NULL,
  `sname` varchar(45) DEFAULT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `lastcall` datetime DEFAULT NULL,
  `laststatus` varchar(45) DEFAULT NULL,
  `needredial` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq-call` (`year`,`nmonth`,`day`,`hours`,`minutes`,`fname`,`sname`,`phone`),
  KEY `idx_name` (`fname`,`sname`),
  KEY `idx_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
