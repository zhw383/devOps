#!/usr/bin/python
# -*- coding=utf-8 -*-
# version: 0.1


import requests
import json
import time

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime
import time
import os,re


def add(x,y):
    return x+y

class tsdbApi(object):
	def __init__(self,platform,line,metric):
		self.platform=platform
		self.line=line
		self.metric=metric

	def getVedioUrl(self):
		#昨天的时间点
		startTime= datetime.datetime.combine(datetime.date.today()+ datetime.timedelta(days=-1), datetime.time.min)
		endTime=datetime.datetime.combine(datetime.date.today()+ datetime.timedelta(days=-1), datetime.time.max)
		startTimeStamp1=int(time.mktime(startTime.timetuple()))
		endTimeStamp1=int(time.mktime(endTime.timetuple()))
		tsdbUrl='http://183.36.111.59:4242/api/query?start={startTimeStamp}&end={endTimeStamp}&m={metric}{{sPlatform={platform},line={line}}}'
		tsdbApiUrl=tsdbUrl.format(startTimeStamp=startTimeStamp1,endTimeStamp=endTimeStamp1,platform=self.platform,line=self.line,metric=self.metric)
		print "tsdbApiUrl=",tsdbApiUrl
		r=requests.get(tsdbApiUrl)
		datalist=json.loads(r.text)
		dpsDict=datalist[0]['dps']
		resourceList=[]
		for k,v in dpsDict.iteritems():
			kk=float(k)
			timeArray = time.localtime(kk)
			otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
			resourceList.append(v)
		sum_num=reduce(add,resourceList)
		avg_num=sum_num/len(resourceList)
		if self.metric=="avg:video.video_load_time.line_avg":
			sum_num=int(sum_num)
			avg_num=int(avg_num)
			min_num=int(min(resourceList))
			max_num=int(max(resourceList))
		else:
		#转换为百分号
			sum_num="%.2f %%" % sum_num
			avg_num="%.2f %%" % avg_num
			min_num="%.2f %%" % min(resourceList)
			max_num="%.2f %%" % max(resourceList)
		#邮件内容
		sendContent="<tr><td>"+str(self.platform)+"</td><td>"+str(self.line)+"</td><td>"+str(max_num)+"</td><td>"+str(avg_num)+"</td><td>"+str(min_num)+"</td><td>"+str(sum_num)+"</td></tr>"
		#print sendContent
		return sendContent

def writeFile():
	#将结果写入临时文件
	platformList=['adr','ios']
	#lineList=['0','1','3']
	lineList=['0']
	metricList=['avg:video.video_bad_quality_ratio.line_avg','avg:video.video_load_time.line_avg','avg:video.video_net_loss_ratio.line_avg']
	content1=""
	content2=""
	content3=""
	content=""
	#昨天的时间最小值和最大值获取
	startTime= datetime.datetime.combine(datetime.date.today()+ datetime.timedelta(days=-1), datetime.time.min).strftime('%Y-%m-%d  %H:%M:%S')
	endTime=datetime.datetime.combine(datetime.date.today()+ datetime.timedelta(days=-1), datetime.time.max).strftime('%Y-%m-%d  %H:%M:%S')
	for p in platformList:
		for l in lineList:
			for m in metricList:
				if m=="avg:video.video_bad_quality_ratio.line_avg":
					metric=tsdbApi(p,l,m)
					content=metric.getVedioUrl()
					content1=content1+content
				elif m=="avg:video.video_load_time.line_avg":
					metric=tsdbApi(p,l,m)
					content=metric.getVedioUrl()
					content2=content2+content
				elif m=="avg:video.video_net_loss_ratio.line_avg":
					metric=tsdbApi(p,l,m)
					content=metric.getVedioUrl()
					content3=content3+content
	os.remove('./mailContent.txt')
	fileModel = open('./mailContentModel.txt').readlines() #  list列表
	fileFormal = file('./mailContent.txt',"a") #a 追加 w可写 r只读
	fileFormal.truncate()#清空文件
	#替换文本里的内容
	for fm in fileModel:  #逐行扫描
		f1_line=re.sub("BADQUALITY",content1,fm)
		f2_line=re.sub("STARTTIME",startTime,f1_line)
		f3_line=re.sub("ENDTIME",endTime,f2_line)
		f4_line=re.sub("LOADTIME",content2,f3_line)
		f5_line=re.sub("NETQUALITY",content3,f4_line)
		fileFormal.write(f5_line)
	fileFormal.close()


def sendmail():
	# 第三方 SMTP 服务
	mail_host="smtp.yy.com"  #设置服务器
	mail_user="yy-huya-voice@yy.com"    #用户名
	mail_pass="Huya2017"   #口令
	sender = 'yy-huya-voice@yy.com'
	receivers = ['zhouhuanwen@yy.com','554290721@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
	#receivers = ['zhouhuanwen@yy.com','chenyi1@yy.com','weiwenhan@yy.com','zhangguanshi@yy.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
	#邮件内容
	# mail_content=get_tsdb(platform,line)
	f=open('./mailContent.txt','r')
	ff=f.read().decode('gbk').encode('utf-8')
	print ff
	message = MIMEText(ff, 'html', 'utf-8')
	message['Accept-Language']="zh-CN"
	message['Accept-Charset']="ISO-8859-1,utf-8"
	message['From'] = Header("yy-huya-voice@yy.com", 'utf-8')
	#增加多个收件人
	for receiver in receivers:
		message['To'] =  Header(receiver,'utf-8')
	subject = '虎牙直播移动端质量数据日报'
	message['Subject'] = Header(subject, 'utf-8')
	try:
	    smtpObj = smtplib.SMTP()
	    smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
	    smtpObj.login(mail_user,mail_pass)
	    smtpObj.sendmail(sender, receivers, message.as_string())
	    print "邮件发送成功"
	except smtplib.SMTPException:
	    print "Error: 无法发送邮件"

if __name__ == "__main__":
	writeFile()
	sendmail()


