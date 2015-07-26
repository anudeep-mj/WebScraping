__author__ = 'Anudeep'

from selenium import webdriver
import csv
from selenium.webdriver.common.by import By


# take input for the maximum number of doctors to be scrapped
data = input("Enter a the maximum number of doctors to be scrapped: (1-246)")
intdata = int(data)

# Check if the value entered is in the range.
if (intdata < 1) or (intdata > 246):
    print "Value entered lesser than 1 or greater than 246. Exiting program."
    exit()

# call the firefox driver
driver = webdriver.Firefox()
driver.get("http://www.witham.org/body.cfm?id=12")


NEXT_BUTTON_XPATH = '//input[@value="Find"]'
listOfNamesOfDoctors = []
data = []
cols_names = []

# function to go to the page with all doctors
def goToHome():
    button = driver.find_element_by_xpath(NEXT_BUTTON_XPATH)
    button.click()

# function to get all doctors in a list of web elements.
def getAllDoctors():
    for names in driver.find_elements_by_css_selector("a.metalist"):
        listOfNamesOfDoctors.append(names.text)

# function to click on a doctor to go into the details
def detailsOfDoctor(doctorName):
    driver.find_element_by_xpath('//*[contains(text(), "%s")]' % doctorName).click()

# special function to split the string in 'Speciality'
def splitForSpeciality(s):
    if ';' in s:
        return "[{}]".format(",".join(map('"{}"'.format, s.split(";"))))

# special function to split the string in 'Certification'
def splitForCertification(s):
    if ',' in s:
        return "[{}]".format(",".join(map('"{}"'.format, s.split(","))))

# got to home
goToHome()

# get all doctors page
getAllDoctors()


pos = 0

# iterating on every doctor in the list of all doctors elements
for eachDoctorName in listOfNamesOfDoctors:

    # go into the doctor page to get the details
    detailsOfDoctor(eachDoctorName)
    eachDoctorName.replace("'", "''")

    # get the details of each doctor and place the web elements on lists.
    insideDetailsOfValues = driver.find_elements_by_xpath("//td[@class='metadetail']")
    insideDetailsOfColumns = driver.find_elements_by_xpath("//th[@class='metadetail']")

    # variable lists to hold the string values of the columns and values of each doctor
    insideDetailsOfColumnsText = []
    insideDetailsOfValuesText = []


    specialityPosition = 0
    specialityPositionFound = 0
    certificationPosition = 0
    certificationPositionFound = 0


    for detail1 in insideDetailsOfColumns:
        # check if the 'Speciality' column is being parsed
        if detail1.text.strip() == "Specialty":
            specialityPositionFound = specialityPosition

        # check if the 'Certification' column is being parsed
        elif detail1.text.strip() == "Certification":
            certificationPositionFound = certificationPosition

        # pointers to iterate to get specialities and certifications
        specialityPosition = specialityPosition + 1
        certificationPosition = certificationPosition + 1

        insideDetailsOfColumnsText.append(detail1.text.encode('utf-8'))

    # To have the 'Doctor Name' Column
    insideDetailsOfColumnsText.insert(0, 'Doctor Name'.encode('utf-8'))

    specialityValuePosition = 0
    certificationValuePosition = 0


    for detail2 in insideDetailsOfValues:
        # logic to format the string being inserted in the csv file for 'Speciality'
        if specialityValuePosition == specialityPositionFound + 1:
            if ';' in detail2.text:
                temptext1 = splitForSpeciality(detail2.text)
                insideDetailsOfValuesText.append(temptext1.encode('utf-8'))
            else:
                temptext1 = '["' + detail2.text + '"]'
                insideDetailsOfValuesText.append(temptext1.encode('utf-8'))

        # logic to format the string being inserted in the csv file for 'Certification'
        elif certificationValuePosition == certificationPositionFound + 1:
            if ',' in detail2.text:
                temptext2 = splitForCertification(detail2.text)
                insideDetailsOfValuesText.append(temptext2.encode('utf-8'))
            else:
                temptext2 = '["' + detail2.text + '"]'
                insideDetailsOfValuesText.append(temptext2.encode('utf-8'))

        else:
            insideDetailsOfValuesText.append(detail2.text.encode('utf-8'))

        certificationValuePosition = certificationValuePosition + 1
        specialityValuePosition = specialityValuePosition + 1

    # build data with all the details as dictionaries
    data.append(dict(zip(insideDetailsOfColumnsText, insideDetailsOfValuesText)))

    driver.get("http://www.witham.org/body.cfm?id=12")
    goToHome()

    # checks the loop for the maximum number of doctor specified
    pos = pos + 1
    print 'Doctor %d scrapped' %(pos)
    if pos > (intdata - 1):
            break
    # the above four lines (except for the printing line) to be indented if all the data is to be scrapped


    for col in insideDetailsOfColumnsText:
        if col not in cols_names:
            cols_names.append(col)



# File created for writing the data.
test_file = open('HealthServices_Scrape.csv', 'wb')

# Writing the .csv file
writer = csv.DictWriter(test_file, list(cols_names))
writer.writeheader()
for page in data:
    writer.writerow(page)
