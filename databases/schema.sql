CREATE TABLE `PasteFile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(5000) NOT NULL,
  `filehash` varchar(128) NOT NULL,
  `uploadTime` datetime NOT NULL,
  `mimetype` varchar(256) NOT NULL,
  `symlink` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `size` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `filehash` (`filehash`),
  UNIQUE KEY `symlink` (`symlink`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
