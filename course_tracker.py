import requests
import time
import smtplib
from bs4 import BeautifulSoup
from email.message import EmailMessage
#from alert import email_alert

# change these values to correspond to your phone number and semester
email_to = ""
semester = "202301"
url = "https://usfweb.usf.edu/DSS/StaffScheduleSearch/StaffSearch/Results"
timeDelay = 10

labels = {'SESSION': 0, 'COL': 1, 'DPT': 2, 'CRN': 3, 'SUBJCRS#': 4, 'SEC': 5, 'TYPE': 6, 'TITLE': 7, 'CR': 8,
				'PMT': 9, 'STATUS': 10, 'STATUS2': 11, 'SEATSREMAIN': 12, 'WAITSEATSAVAIL': 13, 'CAP': 14, 'ENRL': 15, 'DAYS': 16,
				'TIME': 17, 'BLDG': 18, 'ROOM': 19, 'INSTRUCTOR': 20, 'CAMPUS': 21, ' DELIVERY METHOD ': 22, '  FEES ': 23}

def get_classes(payload):
	r = requests.post(url, data=payload)
	soup = BeautifulSoup(r.text, "lxml")
	table = soup.find(id="results").find_all("tr")
	table.pop(0)
	classes = [row.find_all("td") for row in table]
	#labels = {k.text:v for v,k in enumerate(table[0].find_all("th"))}
	return classes

# function to send text message in the form of an email
def email_alert(subject, body, to):
	user = ""
	password = ""

	msg = EmailMessage()
	msg.set_content(body)
	msg['subject'] = subject
	msg['to'] = to
	msg['from'] = user

	server = smtplib.SMTP("smtp.gmail.com", 587)
	server.starttls()
	server.login(user, password)
	server.send_message(msg)
	server.quit()

def format_class_info(data):
	output = ""
	for row in data:
		output += "-----------------------------------------------\n"
		output += f"Course: {row[labels['SUBJCRS#']].text}" + "\n"
		output += f"Title: {row[labels['TITLE']].text}" + "\n"
		output += f"CRN: {row[labels['CRN']].text}" + "\n"
		output += f"Status: {row[labels['STATUS']].text}" + "\n"
		output += f"CAP: {row[labels['CAP']].text}" + "\n"
		output += f"ENRL: {row[labels['ENRL']].text}" + "\n"
		output += f"Seats Left: {row[labels['SEATSREMAIN']].text}" + "\n"
		output += f"Days: {row[labels['DAYS']].text}" + "\n"
		output += f"Time: {row[labels['TIME']].text}" + "\n"
		output += f"BLDG: {row[labels['BLDG']].text}" + "\n"
		output += f"ROOM: {row[labels['ROOM']].text}" + "\n"
		output += f"Campus: {row[labels['CAMPUS']].text}" + "\n"
		output += f"Instructor: {row[labels['INSTRUCTOR']].text}" + "\n"
		output += "-----------------------------------------------\n\n"
	return output

def get_user_input():
	subject = input("What is the course subject?: ")
	number = input("Course Number: ")
	online_only = input("Online only Courses?(y/n): ")

	payload = {"P_SEMESTER":semester, "p_status": "O", "p_ssts_code":"A",
				"P_SUBJ":subject, "P_NUM":number, "p_insm_x_inad":"YAD"}

	if(online_only.lower()[0] == "n"):
		payload["p_insm_x_incl"] = "YCL"
		payload["p_insm_x_inhb"] = "YHB"
		payload["p_insm_x_inpd"] = "YPD"
		payload["p_insm_x_innl"] = "YNULL"
		payload["p_insm_x_inot"] = "YOT"

	return {"subject": subject, "number":number, "payload":payload}

def main():
	print("Welcome to Tyler's USF Course Query Program.")
	print("This program is useful in finding the classes you need and will track courses that are full")
	print("Once a space opens up for a course you are tracking, you will be notified via text message.")
	print("-------------------------------------------------------------------------------------------\n")

	user_input = get_user_input()

	while(True):
		classes = get_classes(user_input["payload"])
		num_classes = len(classes)
		if(num_classes > 0):
			msg = format_class_info(classes)
			email_alert(user_input["subject"] +" "+ user_input["number"] + " Spot Available", msg, email_to)
			print("\n")
			print(user_input["subject"] +" "+ user_input["number"] + " Spot Available")
			print("=============================================\n\n")
			print(msg)
			print(f"Total Classes Found: {num_classes}\n\n\n\n")

			if(input("Would you like to search for another course?(y/n) ").lower()=="y"):
				user_input = get_user_input()
				continue
			else:
				print("\nThanks for using Tyler's USF Course Query.")
				break
		else:
			print(f"Classes are currently full for this course. Will check capacity again in {timeDelay} seconds.")

		time.sleep(timeDelay)

if __name__ == "__main__":
	main()
