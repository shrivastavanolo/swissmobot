import sys
import os
import time
import requests
import pickle
import subprocess
from bs4 import BeautifulSoup

def fetch_emploment_details(page_number: int, employment_type: str):
    
    global filename
    if employment_type == 'internship':
        filename = "internship_details.txt"
    elif employment_type=='job':
        filename = "job_details.txt"
            
    try:
        # x = 3/0 # zero division error to go into except
        url = 'https://internshala.com/employer/paginated_jobs'

        # Load cookies from a file
        with open('internshala_automation.pkl', 'rb') as f:
            loaded_cookies = pickle.load(f)

        # Debug: Print the loaded cookies to inspect their format
        # print("Loaded cookies:", loaded_cookies)

        # Assuming loaded_cookies is a list of dicts, transform it into a single dict
        if isinstance(loaded_cookies, list):
            cookies = {cookie['name']: cookie['value'] for cookie in loaded_cookies}
        else:
            # If already a dict, use as is
            cookies = loaded_cookies

        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        data = {
            'page_number': page_number,
            'employment_type': employment_type,
            'reload_if_no_job_found': 'false'
        }



        # Make the POST request with the cookies
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
            
        # creates an empty file
        with open(filename, 'w'):
            pass
            
        if response.status_code == 200:
            html_content = response.json()['view']
            # print('html: ',html_content)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            job_actions_divs = soup.find_all('div', class_='job-actions')

            slugs = []
            for div in job_actions_divs:
                # Find all anchor tags within the div
                anchor_tags = div.find_all('a')
                # Get the href of every third anchor tag
                for i, anchor in enumerate(anchor_tags, start=1):
                    if i % 3 == 0:  # Check if it's the third anchor tag
                        href = anchor.get('href')
                        # print(href)
                        slugs.append(href)
                        
            packages_in_order = []
            #TODO Make changes in except too
            for slug in slugs:
                current_package = get_packages(slug)
                if current_package != None:
                    packages_in_order.append(current_package)

            print('package:', len(packages_in_order))
            
            if employment_type == 'internship':
                internships = soup.find_all(class_="internship")
                internship_info = []
                
                for internship in internships:
                    text_element = internship.find(class_="text")
                    internship_id = internship.get('id')
                    span = internship.find("span", class_="badge-pill")
                    if span:
                        listing_status = span.text
                    else:
                        listing_status = 'pingu'
                    # saving only Active listings to text file 
                    if text_element is not None and internship_id is not None and listing_status == 'Active':
                        # print(text_element.text.strip(), job_id, listing_status)
                        internship_info.append((text_element.text.strip(), internship_id))
                employment_info = internship_info
                
            else:
                jobs = soup.find_all(class_="job")
                job_info = []
                
                for job in jobs:
                    text_element = job.find(class_="text")
                    job_id = job.get('id')
                    span = job.find("span", class_="badge-pill")
                    if span:
                        listing_status = span.text
                    else:
                        listing_status = 'pingu'
                    # saving only Active listings to text file 
                    if text_element is not None and job_id is not None and listing_status == 'Active':
                        # print(text_element.text.strip(), job_id, listing_status)
                        job_info.append((text_element.text.strip(), job_id))
                # filename = "job_details.txt"
                employment_info = job_info

            # Writing to a file
            with open(filename, 'w', encoding="utf-8") as file:
                if len(packages_in_order) == 0:
                    for count, (name, internship_id) in enumerate(employment_info, start=1):
                        line = f"{count}___{name}___{internship_id}___None\n"
                        # print(line)
                        file.write(line)
                else:
                    for count, (package, (name, internship_id)) in enumerate(zip(packages_in_order, employment_info), start=1):
                        line = f"{count}___{name}___{internship_id}___{package}\n"
                        # print(type(package))
                        file.write(line)
        else:
            print(f"Failed to retrieve data: HTTP {response.status_code}")
            
    except ZeroDivisionError:
        print('inside except')
        process = subprocess.Popen(['python', 'internshala_login.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("OUT: ", stdout)
        print("ERR: ", stderr)

        url = 'https://internshala.com/employer/paginated_jobs'

        # Load cookies from a file
        with open('internshala_automation.pkl', 'rb') as f:
            loaded_cookies = pickle.load(f)

        # Debug: Print the loaded cookies to inspect their format
        # print("Loaded cookies:", loaded_cookies)

        # Assuming loaded_cookies is a list of dicts, transform it into a single dict
        if isinstance(loaded_cookies, list):
            cookies = {cookie['name']: cookie['value'] for cookie in loaded_cookies}
        else:
            # If already a dict, use as is
            cookies = loaded_cookies

        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

        data = {
            'page_number': page_number,
            'employment_type': employment_type,
            'reload_if_no_job_found': 'false'
        }



        # Make the POST request with the cookies
        response = requests.post(url, headers=headers, cookies=cookies, data=data)

        # creates an empty file
        with open(filename, 'w'):
            pass
        
        if response.status_code == 200:
            html_content = response.json()['view']
            soup = BeautifulSoup(html_content, 'html.parser')

            job_actions_divs = soup.find_all('div', class_='job-actions')

            slugs = []
            for div in job_actions_divs:
                # Find all anchor tags within the div
                anchor_tags = div.find_all('a')
                # Get the href of every third anchor tag
                for i, anchor in enumerate(anchor_tags, start=1):
                    if i % 3 == 0:  # Check if it's the third anchor tag
                        href = anchor.get('href')
                        # print(href)
                        slugs.append(href)
            
            packages_in_order = []
            for slug in slugs:
                current_package = get_packages(slug)
                packages_in_order.append(current_package)
            
            if employment_type == 'internship':
                internships = soup.find_all(class_="internship")
                internship_info = []
                
                for internship in internships:
                    text_element = internship.find(class_="text")
                    internship_id = internship.get('id')
                    span = internship.find("span", class_="badge-pill")
                    if span:
                        listing_status = span.text
                    else:
                        listing_status = 'pingu'
                        # saving only Active listings to text file 
                    if text_element is not None and internship_id is not None and listing_status == 'Active':
                        internship_info.append((text_element.text.strip(), internship_id))
                employment_info = internship_info
                
            else:
                jobs = soup.find_all(class_="job")
                job_info = []
                
                for job in jobs:
                    text_element = job.find(class_="text")
                    job_id = job.get('id')
                    span = job.find("span", class_="badge-pill")
                    if span:
                        listing_status = span.text
                    else:
                        listing_status = 'pingu'
                        # saving only Active listings to text file 
                    if text_element is not None and job_id is not None and listing_status == 'Active':
                        job_info.append((text_element.text.strip(), job_id))
                # filename = "job_details.txt"
                employment_info = job_info

            # Writing to a file
            with open(filename, 'w', encoding="utf-8") as file:
                for count, (package, (name, internship_id)) in enumerate(zip(packages_in_order, employment_info), start=1):
                    line = f"{count}___{name}___{internship_id}___{package}\n"
                    # print(line)
                    file.write(line)

        else:
            print(f"Failed to retrieve data: HTTP {response.status_code}")
            
def get_packages(slug):
    url = "https://internshala.com/"+slug
    # print(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        div_with_salary = soup.find('div', class_='item_body salary')
        if div_with_salary:
            desktop_span = div_with_salary.find('span', class_='desktop')
            if desktop_span:
                value = desktop_span.text
                val = " ".join(value.strip().split(" ")[1:])
                # print(val)
                return val
            else:
                    print("No span with class 'desktop' found within div with class 'item_body salary'")
        else:
                print("No div with class 'item_body salary' found in the HTML content")

    else:
            print(f"Failed to retrieve data: HTTP {response.status_code}")
            
            
    pass


if __name__ == "__main__":
    script_name = sys.argv[0]  # Name of the script
    arg1 = sys.argv[1]  # First command-line argument
    arg2 = sys.argv[2] 
    fetch_emploment_details(arg1, arg2)

    # fetch_emploment_details(1, 'internship')
    # package = get_packages('/job/detail/fresher-remote-ai-voice-chatbot-job-at-systemic-altruism1713677691')
    # print(package)
    