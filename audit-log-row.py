#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import pymysql as mysqldb
import os
import time
import sys
import json
import datetime
#执行如下脚本需要修改连接参数
#会自动创建两个用于记录文件最后修改时间和读取文件位置的文件
#安装macfee的MySQL审计插件，并启用会生成如下审计日志；
#该脚本对审计日志进行了拆分，将json数据，按不同列写入MySQL

file_name="/var/lib/mysql/mysql-audit.json"
file_name_rotate="/var/lib/mysql/mysql-audit.json.1"

def check_run():
	#检测pid文件是否存在，存在函数返回为1
	if os.path.exists(path+"/audit.pid"):
		print("pid file exits.")
		return 1
	#如果不存在在创建pid文件，并写入值,函数返回值为0
	else:
		create_pid = open(path+"/audit.pid","w")
		create_pid.write(str(1))
		create_pid.close()
		print("pid file created.")
		return 0

#程序结束后删除pid文件
def del_pid():
	if os.path.exists(path+"/audit.pid"):
		os.remove(path+"/audit.pid")
		print("pid file removed.")
	##
	else:
		print("no pid file.")
	
#..
#获取脚本所在目录
#创建两个文件别记录审计日志的分析位置和mysql-audit.json.1的最后修改时间
path=sys.path[0]

def check_files():
	if os.path.exists(path+"/location.txt"):
		print("location file exits")
	else:
		create_loc = open(path+"/location.txt","w")
		create_loc.write(str(0))
		create_loc.close()
	if os.path.exists(path+"/check_time.txt"):
		print("check_time files exists")
	else:
		create_time = open(path+"/check_time.txt","w")
		create_time.write(str(0))
		create_time.close()
	

#远程数据库连接
db = mysqldb.connect(host="172.16.0.230",user="root",password="xxx",database="xxxx",charset="utf8")


def read_file(file_name):
	
	location_f = open(path+"/location.txt","r",encoding="utf-8")
	location = location_f.readline()
	location_f.close()
	print ('rec loaction:',location)

	location = int(location)
	#创建游标
	cursor = db.cursor() #进行数据库连接i
	#构造
	with open(file_name,"r") as fd:
		fd.seek(location) #将读取文件位置重新定位，初始值在文件中置为0，之后每次将最终位置写入文件进行存储
		for line in fd:
#			print (type(line)) #读取出每行，line的类型为string
#			print (line)
			#将json字符串转换为字典类型
			json_obj=json.loads(line)
#			print(type(json_obj))
#			print(json_obj)
			sql = "insert into audit_row_web(sql_date_time,ip, \
				cmd,db_name,table_name,exe_status,user_name, \
				sql_content,rows_affacted,thread_id,query_id) \
				values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
#			print (sql)
			#使用占位符的方式进行SQL语句拼接,这种方式可以将
			#line中的特殊符号进行转译，避免拼接时发生语法错误

			#获取时间
			date= int(json_obj["date"])/1000
			date_time=datetime.datetime.fromtimestamp(date)
			date_time=date_time.strftime("%Y-%m-%d %H:%M:%S.%f")

			#获取Ip
			try:
				ip = (json_obj["ip"])
			except:
				ip = ''
			else:
				ip = json_obj["ip"]

			#获取命令种类
			try:
				cmd = (json_obj["cmd"])
			except:
				cmd = ''
			else:
				cmd = json_obj["cmd"]

			#根据字典的键取出值,数据库名，数据表名
			try:
				null= (json_obj["objects"][0])
			except:
				db_name = ''
				table_name = ''
			else:
				db_name = json_obj["objects"][0]['db']
				table_name = json_obj["objects"][0]['name']

			#获取执行状态
			try:
				status = int(json_obj["status"])
			except:
				status = '0'
			else:
				status = int(json_obj["status"])


			#获取用户名
			try:
				user = (json_obj["user"])
			except:
				user = ''
			else:
				user = json_obj["user"]


			#获取SQL语句
			try:
				query = (json_obj["query"])
			except:
				query = ''
			else:
				query = json_obj["query"]

			#获取SQL语句影响行数
			try:
				null= int(json_obj["rows"])
			except:
				rows = '0'
			else:
				rows = int(json_obj["rows"])

			#获取线程ID
			try:
				thread_id = int(json_obj["thread-id"])
			except:
				thread_id = '0'
			else:
				thread_id = int(json_obj["thread-id"])

			#获取查询ID
			try:
				query_id = int(json_obj["query-id"])
			except:
				query_id = '0'
			else:
				query_id = int(json_obj["query-id"])

			cursor.execute(sql,(date_time,ip,cmd,\
			db_name,table_name,status,user,\
			query,rows,thread_id,query_id))

			cursor.execute("commit")
		location = fd.tell()                            #记录最后一次读取文件的位置
	#关闭游标
	cursor.close()
		#将记录写入文件
		#在下次读取时获得增量，location变量为数值类型
#		print (location)
	print ("new location:",location) #可以打印
	#将location的值存储在文本文件中以便下次使用；
	location_f = open(path+"/location.txt","w",encoding="utf-8")
	location_f.write(str(location))   #无法再文本文件中存储数值类型，需将器转换成字符串类型
	location_f.close()


#考虑日志轮换的问题
#mysql-audit.json一直在更新，在文件增长到一定程度后，
#日志进行轮换，mysql-audit.json重命名为mysql-audit.json.1
#新建一个mysql-audit.json，开始写入新的日志；
#如果读mysql-audit.json就会遇到在切换日志时，可能会有未处理的日志，
#如果读mysql-audit.json.1就会有较长时间的延时1天；
#检测mysql-audit.json.1的修改时间
#根据其变化进行不同操作，以便获取正确的日志内容

def check_time():
	print('script loaction :',path)
	#检测"/var/lib/mysql/mysql-audit.json.1"最后修改时间
	json_time_now=os.path.getmtime(file_name_rotate)
	#将值转换为int
	json_time_now=int(json_time_now)

	print("audit log modify time now",json_time_now)

	#读取check_time.txt文件中的内容，文件中初始值为0
	time_rec = open(path+"/check_time.txt","r",encoding="utf-8")
	json_time_rec = time_rec.readline()
	#将字符串转换为int

#	print("rec",json_time_rec)
	json_time_rec=int(json_time_rec)
	print("audit log modify time rec",json_time_rec)

	#将本次解析文件时间存储在check_time.txt中，默认格式为小数点后四位；
	#将其转换为int，并按照字符串存储在文件中,用于下次比较
	time_f = open(path+"/check_time.txt","w",encoding="utf-8")
	time_f.write(str(json_time_now))
	time_f.close()
	if json_time_rec == 0:
		return -1
	elif json_time_rec == json_time_now:
		return 1
	else:
		return 0

#如下为主逻辑函数
#根据记录时间的不同，分别执行不同函数
#第一次执行前check_time.txt将中内容置为0，将会直接执行如下函数
def main():
	print("start analysing audit log ....")	
	print (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
	#检测pid文件是否存在
	run = check_run()
	#若果存在，则退出程序
	if run == 1:
		print("programe is running! exit")

	#若果不存在，则执行读取文件，写入数据库操作
	else:
		#首先检查两个文件是否存在，如果存在将不做任何操作，
		#如果不存在则创建两个文件，并写入初始值
		check_files()  
#		time.sleep(10)	
		#检查日志文件的更改时间，根据是否轮换，进行不同操作
		status = check_time()
	
		if status == -1:
			read_file(file_name)
			print("first time auditing",0)

		#之后执行时，将比较记录时间和当前时间
		#如果时间相同，表明没有进行日志的轮换
		#可以相关参数不改变，可以继续执行
		elif status == 1:
			read_file(file_name)
			print("audit log file was not changed.")

		#如果发生日志切换
		else:
			#首先解析的文件名需要调整，但是文件的偏移量不需更改
			read_file(file_name_rotate)
			#执行完成后，因为此时/mysql/mysql-audit.json为一个新文件，需要从头解析
			#重写location值，置为0，再次执行
			location_f = open(path+"/location.txt","w",encoding="utf-8")
			location_f.write(str(0))
			location_f.close()
	
			read_file(file_name)
			print("audit log was rotated.")
		#关闭连接
		db.close()
	#删除pid文件
	del_pid()
	#打印当前时间
#	print (time.localtime(time.time()))
	print('analyzing audit log ended .')
	print (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
if __name__ == '__main__':
	main()

