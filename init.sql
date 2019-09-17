-- 创建数据库

create database audit;
use audit;
-- 建表语句
CREATE TABLE `audit_row_web` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `sql_content` text NOT NULL COMMENT 'SQL语句',
  `sql_date_time` datetime(6) NOT NULL DEFAULT '0000-00-00 00:00:00.000000' COMMENT 'SQL执行时间',
  `ip` varchar(32) NOT NULL DEFAULT '0' COMMENT '用户ip',
  `thread_id` int(11) NOT NULL DEFAULT '0' COMMENT '线程id',
  `query_id` int(11) NOT NULL DEFAULT '0' COMMENT '查询id',
  `cmd` varchar(16) NOT NULL COMMENT '命令类型',
  `db_name` varchar(32) NOT NULL DEFAULT '' COMMENT 'SQL作用的数据库',
  `table_name` varchar(32) NOT NULL DEFAULT '' COMMENT 'SQL作用的数据表名',
  `exe_status` int(11) NOT NULL COMMENT '语句执行状态:0为执行成功，其他为报错',
  `user_name` varchar(16) NOT NULL COMMENT '用户名',
  `rows_affacted` int(11) NOT NULL DEFAULT '0' COMMENT 'SQL语句影响行数',
  PRIMARY KEY (`id`),
KEY `idx_sql_date_time` (`sql_date_time`),
KEY `idx_table_name` (`table_name`)
) ENGINE=TokuDB  DEFAULT CHARSET=utf8;
