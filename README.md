# audit-script-macfee
A script to analyse audit-log and push to mysql-db. You need to install the plugin libaudit_plugin.so and set the loging on first.

libaudit_plugin.so版本5.7.25

依赖环境pymysql(python3)/mysqldb(python2)

社区版本MySQL是不带有审计功能的，想要实现审计功能，记录特定的SQL语句，需要通过安装插件实现

一、对应软件下载地址：(2019-08-07-截止该日期，目前支持MySQL社区版5.7.25及之前版本)

https://dl.bintray.com/mcafee/mysql-audit-plugin/

二、选择对应mysql版本

audit-plugin-mysql-5.7-1.1.7-821-linux-x86_64.zip

三、查看mysql的plugin_dir;
```mysql
mysql> show global variables like 'plugin_dir';
+---------------+-------------------------------------+
| Variable_name | Value |
+---------------+-------------------------------------+
| plugin_dir | /kingsql/database/mysql/lib/plugin/ |
+---------------+-------------------------------------+
1 row in set (0.00 sec)
```
四、进行解压：

五、将解压目录中的libaudit_plugin.so文件拷贝的上述目录下

六、增加执行权限
```sh
ubuntu@et-dba-tianzhaofeng:/kingsql/database/mysql/lib/plugin$ sudo chmod +x libaudit_plugin.so
```
七、改变该文件所属用户及组：
```sh
ubuntu@et-dba-tianzhaofeng:/kingsql/database/mysql/lib/plugin$ sudo chown -R mysql:mysql /kingsql/database/mysql/lib/plugin
```
八、进行安装、在进入mysql中，输入如下命令
```mysql
mysql> INSTALL PLUGIN AUDIT SONAME 'libaudit_plugin.so';
```
Query OK, 0 rows affected (10.80 sec)


九、查看审计文件名；
```mysql
mysql> show global variables like 'audit_json_log_file';
+---------------------+------------------+
| Variable_name | Value |
+---------------------+------------------+
| audit_json_log_file | mysql-audit.json |
+---------------------+------------------+
1 row in set (0.00 sec)
```
十、查看是否开启审计功能
```mysql
mysql> show global variables like 'audit_json_file';
+-----------------+-------+
| Variable_name | Value |
+-----------------+-------+
| audit_json_file | OFF |
+-----------------+-------+
1 row in set (0.00 sec)
```
十一、设置审计文件记录信息
```mysql
set global audit_record_cmds="insert,delete,update,create_table,create_user,drop_table,drop_user,drop_db,create_db,alter_table ,grant, truncate";
```
十二、开启审计功能；
```mysql
set global audit_json_file =1;
show global variables like 'audit_json_file';
+-----------------+-------+
| Variable_name | Value |
+-----------------+-------+
| audit_json_file | ON |
+-----------------+-------+
```
十三、此时可以查看mysql-audit.json文件内容，可以发现对上述命令进行了记录；

使用该方法，可以不对mysql进行重启；
在生产环境中推荐使用。

当然也可以在my.cnf

中增加相关配置，进行数据库重启，同样可以开始改功能。

十四、更改完成后，将配置文件对应参数更改，防止重启MySQL后，导致参数失效

配置文件：
```
plugin-load=AUDIT=libaudit_plugin.so
audit_json_file = 1
audit_record_cmds = 'insert,delete,update,create_table,create_user,drop_table,drop_user,drop_db,create_db,alter_table ,grant, truncate'
```

经测试发现：alter / create / drop 等DDL不会记录到审计日志中

只有select ,delete, truncate ,update,insert 等DML会记录到日志中

十五、通过将audit_record_cmds参数设置为空，将会记录所用的SQL记录；

发现如果想要记录alter / create / drop等失去了需要安装如下参数更改audit_record_cmds
```mysql
set global audit_record_cmds = "insert,delete,update,create_table,create_user,drop_table,drop_user,drop_db,create_db,alter_table ,grant, truncate";
```
