#!/usr/bin/python3
import praw #reddit python api
import boto3 #aws python api
import requests
import config

#AWS creds

polly_client = boto3.Session(
				aws_access_key_id=config.aws_access,
				aws_secret_access_key=config.aws_secret,
				region_name='us-east-1').client('polly')
s3 = boto3.resource('s3')


enseAuth = 'Bearer ' + config.enseKey


reddit = praw.Reddit(user_agent='ensebot',
					client_id=config.cID,
					client_secret=config.cSC,
					username=config.userN,
					password=config.userP)

def ense():
		response = polly_client.start_speech_synthesis_task(
			Engine='standard',
			LanguageCode='en-US',
			OutputFormat='mp3',
			OutputS3BucketName=config.s3bucket,
			Text=speechtext,
			TextType='text',
			VoiceId='Joanna'
		)

		#Sends text to speech engine and streams output to s3 bucket

		taskId = response['SynthesisTask']['TaskId'] #get task ID
		print("Task id is " + taskId)
		uploadedURI = response['SynthesisTask'] ['OutputUri'] #get url of uploaded file
		print ("URI is " + uploadedURI)

#post to ense
		enseheaders = {
			   'Authorization': enseAuth,
		}

#data for ense request
		ensedata = {
			'title': enseTitle,
			'fileUrl': uploadedURI,
			'unlisted': 'false',
			'mimeType': 'mp3',
			'delayRelease': 'false'
		}
#ense request
		enseresponse = requests.post('https://api.ense.nyc/ense/lip', headers=enseheaders, data=ensedata)
		print ("request sent to ense")
		ensereply = enseresponse.json()
		dbkeyreply = ensereply ['contents'] ['dbKey']
		enseurl = "https://pro.ense.nyc/ense/" + dbkeyreply + "/lip"
		comment.reply("Here is an ense of that comment: " + enseurl)
		print ("Comment reply completed. Here is a link to the ense \n" + enseurl)
		print (enseTitle)
		print("upload complete")


#### Can be used to get user inout to specify for sub
#subinput = input ("Enter Subreddit\n") #userinput for sub use "all" for sitewide
#print ("Sub is r/" + subinput)
#print ("Listening for "+ '"' + trigger_phrase + '"' + " on r/" + subinput)

trigger_phrase = '!ensebot'
subreddit = reddit.subreddit('all') #any subreddit you want to monitor

for comment in subreddit.stream.comments(): #listens to all comments
	if trigger_phrase in comment.body: #finds trigger phrase
		try:
			if comment.is_root == True:
				if comment.submission.selftext:
					selfsub = comment.submission
					speechtext = selfsub.selftext
					enseTitle = "This is a selftext post on reddit by u/" + comment.submission.author.name + " on  r/" + comment.submission.subreddit.display_name
					ense()
				else:
					print('not a self post')
					continue
			elif comment.is_root == False:
				parent = comment.parent() #gets parent comment
				speechtext = parent.body #sets string to the body object of the parent which is text in markdown
				parentcommentlink = parent.permalink
				print(comment.submission.title + " uploading")
				enseTitle = "This is a comment on reddit by u/" + parent.author.name + " on  r/" + parent.subreddit.display_name + " Here is a link to the original comment: https://reddit.com" + parentcommentlink
				ense()
			else:
				continue

		except AttributeError:
			print("Something went wrong.")
			continue
