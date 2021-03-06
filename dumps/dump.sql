CREATE DATABASE IF NOT EXISTS bitshares;
USE bitshares;
CREATE TABLE IF NOT EXISTS `p2pbridge_exchange_rates_source` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `FREQUENCY` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=311 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS `p2pbridge_assets` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ASSET_ID` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `SYMBOL` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `TYPE_ID` int(11) NOT NULL,
  `MARKET` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `ACTIVE` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `ISSUE` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `PRECESION` int(11) DEFAULT NULL,
  `PRECISION_DEALS` int(11) DEFAULT NULL,
  `PRECISION_RATES` int(11) DEFAULT NULL,
  `COINMARKETCAP_CODE` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `MAX_MARKET_FEE` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `MAX_SUPPLY` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `COINMARKETCAP_ID` int(11) NOT NULL,
  `MONITOR` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `SORT` int(11) DEFAULT NULL,
  `LOGO` int(11) DEFAULT NULL,
  `DEVELOP` varchar(1) COLLATE utf8_unicode_ci DEFAULT 'N',
  `DATE_CREATE` datetime DEFAULT '2018-01-01 10:00:00',
  `COMMISSION_IN_TRANSACTION` float DEFAULT NULL,
  `COMMISSION_OUT_TRANSACTION` float DEFAULT NULL,
  `IMF_NAME` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=311 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS `p2pbridge_exchange_rates_meta` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `SOURCE_ID` int(11) DEFAULT NULL,
  `BASE_ASSET_ID` int(11) DEFAULT NULL,
  `QUOTE_ASSET_ID` int(11) DEFAULT NULL,
  `MARKET_ASSET_ID` int(11) DEFAULT NULL,
  `ACTIVE` varchar(50) COLLATE utf8_unicode_ci DEFAULT 'N',
  `BASE_ASSET_TEXT` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `QUOTE_ASSET_TEXT` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `NAME` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `SYMBOL` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `DESCRIPTION` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `POPULAR` varchar(1) COLLATE utf8_unicode_ci NOT NULL DEFAULT 'N',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE IF NOT EXISTS `p2pbridge_exchange_rates_values` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `RATE_ID` int(11) DEFAULT NULL,
  `DATETIME` datetime NOT NULL,
  `VALUE` double NOT NULL,
  `ACTIVE` varchar(1) COLLATE utf8_unicode_ci DEFAULT 'N',
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=72428 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
INSERT INTO p2pbridge_exchange_rates_source (ID,NAME,FREQUENCY) VALUES
(311,'bitshares',5)
,(312,'coinmarketcap',5)
,(313,'cbrf',720)
,(314,'mmvb',5)
,(315,'imf',720);
INSERT INTO p2pbridge_assets (ID,ASSET_ID,SYMBOL,TYPE_ID,MARKET,ACTIVE,ISSUE,PRECESION,PRECISION_DEALS,PRECISION_RATES,COINMARKETCAP_CODE,MAX_MARKET_FEE,MAX_SUPPLY,DESCRIPTION,COINMARKETCAP_ID,MONITOR,SORT,LOGO,DEVELOP,DATE_CREATE,COMMISSION_IN_TRANSACTION,COMMISSION_OUT_TRANSACTION,IMF_NAME) VALUES 
(212,'1.3.0','BTS',3,'','Y','1.2.3',5,1,4,'BTS','1000000000000000','360057050210207','',463,'Y',4,96,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(213,'1.3.121','bitUSD',1,'','Y','1.2.0',4,2,4,'BITUSD','1000000000000000','1000000000000000','1 United States dollar',623,'Y',1,95,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(214,'1.3.861','OPEN.BTC',2,'','N','1.2.96397',8,8,8,NULL,'1000000000000000','1000000000000000','OpenLedger Bitcoin-backed asset - https://openledger.info/',0,'Y',6,97,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(230,'1.3.103','bitBTC',1,'','Y','1.2.0',8,8,8,'BITBTC','1000000000000000','1000000000000000','1 bitcoin',625,'Y',5,92,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(291,'','RUB',4,'','Y','',0,0,4,'RUB','','','Рубль',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,'Russian ruble')
,(292,'','USD',4,'','Y','',0,2,4,'USD','','','Доллар',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,'U.S. dollar')
,(293,'1.3.1325','bitRUBLE',1,'','Y','1.2.0',5,0,4,NULL,'0','1000000000000000','bitRUBLE',0,'Y',2,94,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(294,' ','EURO',4,'','Y',' ',0,2,4,'EUR',' ',' ','Euro',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,'Euro')
,(295,' ','CNY',4,'','Y',' ',0,1,4,'CNY',' ',' ','CNY',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,'Chinese yuan')
,(296,'0','BTC',4,'','Y','0',0,8,8,'BTC','0','0','BTC',1,'N',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(297,'0','ETH',4,'','Y','0',0,6,6,'ETH','0','0','ETH',1027,'N',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(298,'0','KRW',4,'','Y','0',0,1,4,'KRW','0','0','KRW',0,'N',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(299,'1.3.0','KRM',3,'','Y','1.2.0',5,0,4,'KRM','1000000000000000','1000000000000000','Karma',2378,'Y',7,136,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(307,'','MILE',3,'','Y','1.2.0',5,5,4,NULL,'','','Mile',0,'N',8,0,'Y','2018-01-01 15:00:00.000',NULL,0.002,NULL)
,(308,'','XDR',3,'','N','1.2.0',5,5,4,NULL,'','','Stable coin in Mile',0,'N',9,0,'Y','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(309,'1.3.2387','OPEN.KRM',1,'','N','1.2.0',8,0,4,'KRM',NULL,NULL,'',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
,(310,'1.3.2672','RUDEX.KRM',1,'','N','1.2.0',8,0,4,'KRM',NULL,NULL,'',0,'Y',NULL,NULL,'N','2018-01-01 15:00:00.000',NULL,NULL,NULL)
;
INSERT INTO p2pbridge_exchange_rates_meta (ID,SOURCE_ID,BASE_ASSET_ID,QUOTE_ASSET_ID,MARKET_ASSET_ID,ACTIVE,BASE_ASSET_TEXT,QUOTE_ASSET_TEXT,NAME,SYMBOL,DESCRIPTION,POPULAR) VALUES 
(0,312,297,292,297,'Y',NULL,NULL,NULL,'cmc_eth_usd',NULL,'N')
,(27,311,212,213,NULL,'Y',NULL,NULL,NULL,'bts_bts_usd',NULL,'N')
,(28,311,211,213,NULL,'Y',NULL,NULL,NULL,'bts_cny_usd',NULL,'N')
,(29,311,214,213,NULL,'Y',NULL,NULL,NULL,'bts_openbtc_usd',NULL,'N')
,(30,311,230,213,NULL,'Y',NULL,NULL,NULL,'bts_bitbtc_usd',NULL,'N')
,(31,311,213,293,NULL,'Y',NULL,NULL,NULL,'bts_usd_rub',NULL,'N')
,(32,311,310,212,NULL,'Y',NULL,NULL,NULL,'bts_rudexkrm_bts',NULL,'N')
,(33,311,211,212,NULL,'Y',NULL,NULL,NULL,'bts_cny_bts',NULL,'N')
,(34,311,214,212,NULL,'Y',NULL,NULL,NULL,'bts_openbtc_bts',NULL,'N')
,(35,311,230,212,NULL,'Y',NULL,NULL,NULL,'bts_bitbtc_bts',NULL,'N')
,(36,311,212,293,NULL,'Y',NULL,NULL,NULL,'bts_bts_rub',NULL,'N')
,(37,312,211,292,NULL,'Y',NULL,NULL,NULL,'cmc_bitcny_usd',NULL,'N')
,(38,312,212,292,NULL,'Y',NULL,NULL,NULL,'cmc_bts_usd',NULL,'N')
,(39,312,213,292,NULL,'Y',NULL,NULL,NULL,'cmc_bitusd_usd',NULL,'N')
,(40,312,296,292,NULL,'Y',NULL,NULL,NULL,'cmc_btc_usd',NULL,'N')
,(41,312,230,292,NULL,'Y',NULL,NULL,NULL,'cmc_bitbtc_usd',NULL,'N')
,(42,312,299,292,NULL,'Y',NULL,NULL,NULL,'cmc_krm_usd',NULL,'N')
,(43,312,211,212,NULL,'Y',NULL,NULL,NULL,'cmc_bitcny_bts',NULL,'N')
,(45,312,213,212,NULL,'N',NULL,NULL,NULL,'cmc_bitusd_bts',NULL,'N')
,(46,312,212,296,NULL,'Y',NULL,NULL,NULL,'cmc_bts_btc',NULL,'N')
;
INSERT INTO p2pbridge_exchange_rates_meta (ID,SOURCE_ID,BASE_ASSET_ID,QUOTE_ASSET_ID,MARKET_ASSET_ID,ACTIVE,BASE_ASSET_TEXT,QUOTE_ASSET_TEXT,NAME,SYMBOL,DESCRIPTION,POPULAR) VALUES 
(47,312,212,230,NULL,'Y',NULL,NULL,NULL,'cmc_bts_bitbtc',NULL,'N')
,(48,312,299,212,NULL,'Y',NULL,NULL,NULL,'cmc_krm_bts',NULL,'N')
,(49,313,292,291,291,'Y',NULL,NULL,NULL,'cbrf_usd_rub',NULL,'N')
,(50,313,294,291,291,'Y',NULL,NULL,NULL,'cbrf_eur_rub',NULL,'N')
,(51,313,295,291,295,'Y',NULL,NULL,NULL,'cbrf_cny_rub',NULL,'N')
,(52,314,292,291,291,'Y',NULL,NULL,NULL,'mmvb_usd_rub',NULL,'N')
,(53,314,294,291,291,'Y',NULL,NULL,NULL,'mmvb_eur_rub',NULL,'N')
,(54,314,295,291,291,'Y',NULL,NULL,NULL,'mmvb_cny_rub',NULL,'N')
,(55,311,309,213,NULL,'Y',NULL,NULL,NULL,'bts_openkrm_usd',NULL,'N')
,(56,311,310,213,NULL,'Y',NULL,NULL,NULL,'bts_rudexkrm_usd',NULL,'N')
,(57,312,211,298,298,'Y',NULL,NULL,NULL,'cmc_bitcny_krw',NULL,'N')
,(58,312,212,298,298,'Y',NULL,NULL,NULL,'cmc_bts_krw',NULL,'N')
,(59,312,213,298,298,'Y',NULL,NULL,NULL,'cmc_bitusd_krw',NULL,'N')
,(60,312,296,298,298,'Y',NULL,NULL,NULL,'cmc_btc_krw',NULL,'N')
,(61,312,230,298,298,'Y',NULL,NULL,NULL,'cmc_bitbtc_krw',NULL,'N')
,(62,312,299,298,298,'Y',NULL,NULL,NULL,'cmc_krm_krw',NULL,'N')
,(63,315,308,292,297,'Y',NULL,NULL,NULL,'imf_sdr_usd',NULL,'N')
;
