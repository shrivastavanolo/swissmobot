import requests
import pickle
import subprocess
import json
from datetime import datetime, timedelta
import traceback
from bs4 import BeautifulSoup
import json
import re
from requests_toolbelt import MultipartEncoder
import csv
import sys
import time

if len(sys.argv) != 2:
    print("Usage: python heart_research.py <folder_path>")
    sys.exit(1)

listing_num = str(sys.argv[0])
print(listing_num)
# listing_num = "2448008"
intro_message = ""
invite_message = ""
assignment = ""
process = ''
file_path = 'listings\\intern_listing.csv'
print("we in")

try:
    with open(file_path, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:

            print(row)
            if row['listing'] == str(listing_num):
                assignment = row['assignment']
                process = row['process']
                if row['intro'] != 'NA':
                    intro_message = row['intro']
                if row['invite'] != 'NA':
                    invite_message = row['invite']
except Exception as e:
    print(e)
            
try:  
    if len(invite_message) ==  0:
        invite_message = """Hi {Candidate_name}, 

    We are interested in your profile for internship at Systemic Altruism. Accept our invite to get shortlisted for this opportunity. 

    Thanks,
    Jack Jay
    Systemic Altruism"""
except Exception as e:
    print(e)
try:
    pass
    
    ## Step 1 to invite everyone of internshala database
    try:
        
        application_ids = []
        offset = 0
        while True:
            
            session = requests.Session()

            # The base endpoint for changing the status of applications
            url = 'https://internshala.com/employer/paginated_invitations'

            # Load cookies from the updated file
            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])

            # Headers for the request
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }


            # Correctly formatted data for the POST request body
            data = {
                "internship_id": f"{listing_num}",
                "offset": f"{offset}"
            }

            # Make the POST request with the cookies, headers, and the specified data
            response = session.post(url, headers=headers, data=data)

            # Check the response
            ids = []
            if response.status_code == 200:
                print("Success:", response.text)
                
                # print("Success:", json.load(response.text))
                html_response = json.loads(response.text)['view']
                ids = re.findall(r'class=\"application_id\">(\d+)<\/div>', html_response)
                application_ids = application_ids + ids
                # print(application_ids)
                # with open('internshala_automation_invite_ids.pkl', 'wb') as f:
                #     pickle.dump(session.cookies, f)
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                
            if offset > 500:
                break
            offset = offset + 10
            time.sleep(1)
            
        if len(application_ids)>0:
            # The base endpoint for changing the status of applications
            url = 'https://internshala.com/employer/invitation'

            # application_ids = ['946672832', '946672833']

            # Convert list of application IDs to a comma-separated string
            application_ids_str = ','.join(application_ids)

            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                    
            # Headers for the request
            payload = MultipartEncoder(
                fields={
                    'application_ids': application_ids_str,
                    'referral': 'invitation',
                    'message': f'{invite_message}',
                    'internship_id': f'{listing_num}', ## change
                    'auto_populated_attachments': '[]',
                    'action': 'invite',
                    'recommend_ids': application_ids_str,
                    'page_type': 'application_list_view',
                    'to_invite_top_applicants': 'false'
                }
            )

            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': payload.content_type,
                'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/invite'
            }


            # Correctly formatted data for the POST request body

            # Make the POST request with the cookies, headers, and the specified data
            response = session.post(url, headers=headers, data=payload)

            # Check the response
            if response.status_code == 200:
                print("Success:", response.text)
                # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                #     pickle.dump(session.cookies, f)
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                
            time.sleep(1)


    except:
        traceback.print_exc()
        print("e")
        pass

    
    if process == 'assignment':
        try:
            session = requests.Session()


            # The endpoint for changing the selecting all applications to get their id and updating cookies
            url = f'https://internshala.com/employer/get_data_for_select_all/{listing_num}'


            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                

            # Prepare headers based on the provided headers
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                }


            data = {
                'rows': -1,
                'offset': 0,
                'sid': 'created_at',
                'sord': 'DESC',
                'status': 'open',
                'internshala_filter': 'false'
                }



            response = session.post(url, headers=headers)
            ids = []
            # Check the response
            if response.status_code == 200:
                ids = json.loads(response.text)['applications_id']
                # print(res)

            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
            time.sleep(1)
            print(ids)
            ## to  send message
            if len(ids)>0:
                    
                session = requests.Session()

                # Set the target URL
                if len(intro_message) != 0:
                    url = 'https://internshala.com/chat/send_message_from_employer_dashboard'
                    # application_ids_str = ','.join(ids)
                    application_ids_str = ','.join([str(id) for id in ids])


                    payload = MultipartEncoder(
                        fields={
                            'application_ids': application_ids_str,  # Assuming the API can handle multiple IDs in this field
                            'referral': 'bulk',
                            'message': f'{intro_message}',
                            'internship_id': f'{listing_num}',
                            'auto_populated_attachments': '[]'
                        }
                    )
                    # paylo0

                    headers = {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                        'Content-Type': payload.content_type,
                        'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/open'
                    }

                    response = session.post(url, headers=headers, data=payload)

                    # Check the response
                    if response.status_code == 200:
                        print("Success:", response.text)
                        # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                        #     pickle.dump(session.cookies, f)
                    else:
                        print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")

                
                            # Set the target URL
                time.sleep(1)
                url = 'https://internshala.com/application/change_status/'

                # Load cookies from the updated file
                with open('internshala_automation.pkl', 'rb') as f:
                    loaded_cookies = pickle.load(f)
                    for cookie in loaded_cookies:
                        session.cookies.set(cookie['name'], cookie['value'])

                # Headers as observed from the actual request
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    # 'Cookie': 'your_cookie_string_here',  # Ensure this is updated with your actual cookie string
                    'Referer': f'https://internshala.com/employer/applications/{listing_num}/1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    # Include any other headers observed in the successful request
                }

                # Data payload, manually constructing the query string for multiple 'id[]' values
                data = {
                    'status_change_referral': 'bulk_operator',
                    'change_status_source': 'new_dashboard',
                    'old_status': 'open',
                    'status': 'shortlisted',
                    # The 'id[]' part will be handled separately to ensure proper formatting
                }

                # The IDs need to be formatted in a way the server accepts
                # ids = ['191705174', '191727358']
                id_payload = '&'.join(f'id[]={id_val}' for id_val in ids)

                # Manually constructing the full data payload as a string, including the IDs
                data_encoded = '&'.join([f'{key}={value}' for key, value in data.items()])
                full_payload = f'{data_encoded}&{id_payload}'

                # Making the POST request with the custom payload
                response = session.post(url, headers=headers, data=full_payload)

                
            
                if response.status_code == 200:
                    print("Success:", response.json())
                else:
                    print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
        
                
        except Exception as e:
            traceback.print_exc()
            print(e)
            pass
                
                
                
                
                
        try:
            session = requests.Session()


            # print("we here")
                    
                # session = requests.Session()

            url = f'https://internshala.com/employer/get_data_for_select_all/{listing_num}'


            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                

            # Prepare headers based on the provided headers
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/shortlisted'
                }


            data = {
                'rows': -1,
                'offset': 0,
                'sid': 'created_at',
                'sord': 'DESC',
                'status': 'shortlisted',
                'internshala_filter': 'false'
                }



            response = session.post(url, headers=headers, data=data)
            ids = []
            # Check the response
            if response.status_code == 200:
                print(response.text)
                ids = json.loads(response.text)['applications_id']
                # print(res)

            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
            
            
            print(ids)
            
            if len(ids)>0:
            
                    

                # The base endpoint for sending assignemnt
                url = 'https://internshala.com/employer/assignment_submit'

                # application_ids = ['192355094', '192353578']

                # Convert list of application IDs to a comma-separated string
                # application_ids_str = ','.join(ids)
                application_ids_str = ','.join([str(id) for id in ids])
                # Headers for the request
                submission_deadline_date = datetime.now() + timedelta(days=4)
                # Format the date as 'dd MMM' YY' e.g., '29 Mar' 24'
                submission_deadline_str = submission_deadline_date.strftime('%d %b\' %y')


                payload = MultipartEncoder(
                    fields={
                        'application_ids': application_ids_str,
                        'source': 'created_bulk_operator_shortlisted',
                        'internship_id': f'{listing_num}',
                        'assignment_message': f"{assignment}",
                        'submission_deadline': submission_deadline_str,
                        'auto_populated_attachments': '[]'
                        # 'auto_populated_chat_msg_id': '162868333'
                    }
                )


                headers = {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                        'Content-Type': payload.content_type,
                        'Host':'internshala.com',
                        'Origin':'https://internshala.com',
                        'Referer':f'https://internshala.com/employer/applications/{listing_num}/1/shortlisted'
                    }


                # Correctly formatted data for the POST request body

                # Make the POST request with the cookies, headers, and the specified data
                response = session.post(url, headers=headers, data=payload)

                # Check the response
                if response.status_code == 200:
                        # print("Success:", response.text)
                    print("Assignment sent successfully to all short listed applicants")
                    print('Sleeping for 5 mins... 💤')
                    time.sleep(300)
                        # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                        #     pickle.dump(session.cookies, f)
                else:
                    print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")

                    # Assignment sent successfully to all short listed applicants
                time.sleep(1)

                    
        except:
            traceback.print_exc()
            pass
        
    elif process == 'offer':
        try:
            session = requests.Session()

            ids = []
            # The endpoint for changing the selecting all applications to get their id and updating cookies
            url = f'https://internshala.com/employer/get_data_for_select_all/{listing_num}'


            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                

            # Prepare headers based on the provided headers
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                }


            data = {
                'rows': -1,
                'offset': 0,
                'sid': 'created_at',
                'sord': 'DESC',
                'status': 'open',
                'internshala_filter': 'false'
                }



            response = session.post(url, headers=headers)
            # ids = []
            # Check the response
            if response.status_code == 200:
                ids = ids + json.loads(response.text)['applications_id']
                # print(res)

            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                
                
                
            url = f'https://internshala.com/employer/get_data_for_select_all/{listing_num}'


            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                

            # Prepare headers based on the provided headers
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
                }


            data = {
                'rows': -1,
                'offset': 0,
                'sid': 'created_at',
                'sord': 'DESC',
                'status': 'shortlisted',
                'internshala_filter': 'false'
                }



            response = session.post(url, headers=headers)
            # ids = []
            # Check the response
            if response.status_code == 200:
                ids = ids + json.loads(response.text)['applications_id']
                # print(res)

            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
            time.sleep(1)
            ## to  send message
            if len(ids)>0:
                    
                session = requests.Session()

                # Set the target URL
                if len(intro_message) != 0:
                    url = 'https://internshala.com/chat/send_message_from_employer_dashboard'
                    # application_ids_str = ','.join(ids)
                    application_ids_str = ','.join([str(id) for id in ids])


                    payload = MultipartEncoder(
                        fields={
                            'application_ids': application_ids_str,  # Assuming the API can handle multiple IDs in this field
                            'referral': 'bulk',
                            'message': f'{intro_message}',
                            'internship_id': f'{listing_num}',
                            'auto_populated_attachments': '[]'
                        }
                    )
                    # paylo0

                    headers = {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                        'Content-Type': payload.content_type,
                        'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/open'
                    }

                    response = session.post(url, headers=headers, data=payload)

                    # Check the response
                    if response.status_code == 200:
                        print("Success:", response.text)
                        # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                        #     pickle.dump(session.cookies, f)
                    else:
                        print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")

                
                            # Set the target URL
                time.sleep(1)
                url = 'https://internshala.com/application/change_status/'

                # Load cookies from the updated file
                # with open('internshala_automation_updated_.pkl', 'rb') as f:
                #     loaded_cookies = pickle.load(f)
                #     for cookie in loaded_cookies:
                #         session.cookies.set(cookie.name, cookie.value)

                # Headers as observed from the actual request
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    # 'Cookie': 'your_cookie_string_here',  # Ensure this is updated with your actual cookie string
                    'Referer': f'https://internshala.com/employer/applications/{listing_num}/1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    # Include any other headers observed in the successful request
                }

                # Data payload, manually constructing the query string for multiple 'id[]' values
                data = {
                    'status_change_referral': 'bulk_operator',
                    'change_status_source': 'new_dashboard',
                    'old_status': 'open',
                    'status': 'hired',
                    # The 'id[]' part will be handled separately to ensure proper formatting
                }

                # The IDs need to be formatted in a way the server accepts
                # ids = ['191705174', '191727358']
                id_payload = '&'.join(f'id[]={id_val}' for id_val in ids)

                # Manually constructing the full data payload as a string, including the IDs
                data_encoded = '&'.join([f'{key}={value}' for key, value in data.items()])
                full_payload = f'{data_encoded}&{id_payload}'

                # Making the POST request with the custom payload
                response = session.post(url, headers=headers, data=full_payload)

                
            
                if response.status_code == 200:
                    print("Success:", response.json())
                else:
                    print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    

                
                url = 'https://internshala.com/chat/send_message_from_employer_dashboard'
                application_ids_str = ','.join([str(id) for id in ids])


                payload = MultipartEncoder(
                    fields={
                        'application_ids': application_ids_str,  # Assuming the API can handle multiple IDs in this field
                        'referral': 'bulk',
                        'message': assignment,
                        'internship_id': f'{listing_num}',
                        'auto_populated_attachments': '[]'
                    }
                )
                # paylo0

                headers = {
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Type': payload.content_type,
                    'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/hired'
                }

                response = session.post(url, headers=headers, data=payload)

                # Check the response
                if response.status_code == 200:
                    print("Success:", response.text)
                    # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                    #     pickle.dump(session.cookies, f)
                else:
                    print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                
        except:
            traceback.print_exc()
            pass
           


except:
    print("here")
    pass
   