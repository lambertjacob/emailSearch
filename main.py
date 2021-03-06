import smtplib
from imap_tools import MailBox, AND

#to compile the emails properly 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver

#imported due to newly updated chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 

#updated version to find_elements()
from selenium.webdriver.common.by import By

#for saving passwords not in file
from decouple import config

import time

#config() allows for passwords to be stored in .env file
senderEmailAddress = config('user',default='')
senderEmailPassword = config('pass', default='')

#class for each website
class website:
    def __init__(self, link, name):
        self.link = link
        self.name = name

#try to send the email back to the user when the data has been recieved
def sendEmail(s, b, email):
    try:   
        
        #create a new session with 587 port
        emailsession = smtplib.SMTP('smtp.gmail.com', 587)
        
        #use tls (transport layer security) which ecrypts data sent over internet
        emailsession.starttls()

        emailsession.login(senderEmailAddress, senderEmailPassword)

        subject = s
        body = b

        #combine subject and body parts into message 
        message = MIMEMultipart() 
        message["subject"] = subject
        message.attach(MIMEText(body, "plain"))
        emailToSend = message.as_string()

        emailsession.sendmail(senderEmailAddress, email, emailToSend)

    except Exception as e:
        print(e)

    finally:
        emailsession.quit() 

  
def searchQuestion(url):
    #install new chromedriver in a service object then open 
    websession = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    #search the url
    websession.get(url)

    #get the info based on xpath
    links = websession.find_elements(By.XPATH, '//div[@class=\'yuRUbf\']//a')
    time.sleep(1) #to have a delay to not make google angry
    names = websession.find_elements(By.XPATH,'//div[@class=\'yuRUbf\']//h3')

    #make a class for the number of links on the first page and store in a list
    websites = list()
        
    #add to class 
    for (link, name) in zip(links,names):
        websites.append(website(str(link.get_attribute('href')), str(name.get_attribute('innerHTML'))))
        
    
    #return list of website objects
    return websites


def makeSubjectBody(question, websites):
    subject = question
    body = ""

    #for each pair print them on different lines with a space between each source
    for website in websites:
        body += str(website.name) + "\n" + str(website.link) + "\n\n"
    
    return subject, body


def generateUrl(question):
    urlStart = "https://www.google.com/search?q="
    #string returned needs +'s and not spaces to search
    return urlStart + question.replace(" ", "+")


def newEmail(question, email):
    
    #search the question, get the data, send the email
    web = searchQuestion(generateUrl(question))
    s,b = makeSubjectBody(question, web)
    sendEmail(s, b, email)

    print(s)
    print(b)


#monitoring the email
def getEmails():
    #sign in
    mailbox = MailBox('imap.gmail.com')
    mailbox.login(senderEmailAddress, senderEmailPassword, initial_folder='INBOX')

    #get the new email that has not been read, set to read
    newEmails = mailbox.fetch(criteria=AND(seen=False), mark_seen=True)

    #if there are no new emails
    if not newEmails:
        mailbox.logout()
        return 0,0,0
    
    #get sender, subject, and body of email
    for newEmail in newEmails:
        userEmail = newEmail.from_
        subjectSent = newEmail.subject
        bodySent = newEmail.text
        mailbox.logout()
        return userEmail, subjectSent, bodySent
    
    return 0,0,0
    

def main():
    
    #repeat to take multiple reuwats
    while(1):
        #read unread emails
        email, subject, body = getEmails()

        #if there actually was an email
        if email != 0:
            #send email
            newEmail(subject, email)

        #check inbox after 5 seconds
        time.sleep(5)


if __name__ == "__main__":
    main()