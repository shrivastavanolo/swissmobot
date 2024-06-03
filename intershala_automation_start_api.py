import os
import requests
import asyncio
import pickle
import json
from datetime import datetime, timedelta
import traceback
import json
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from queries import query_get_many, query_get_one
import sys
import time

import database

async def automate(listing_num:str):
    intro_message_text = ""
    invite_message_text = ""
    assignment_text = ""
    process_text = ''
    
    #Finding row with listing, getting assignment, process, if intro , if invite
    current_listing = query_get_one('''SELECT * FROM projects WHERE listing = ?''', [listing_num])
    
    if current_listing:
        print(current_listing['name'])
        if current_listing['assignment']:
            assignment_text = current_listing['assignment']
            # print(assignment)
        if current_listing['intro']:
            intro_message_text = current_listing['intro']
            # print(intro_message)
        if current_listing['invite']:
            invite_message_text = current_listing['invite']
            # print(invite_message)
        if current_listing['process']:
            process_text = current_listing['process']
            # print(process)
        if assignment_text == "":
            print('Assignment is needed')
            print('🔴'*5)
            return
                        
    else:
        print(f'''couldn't find project with listing number: {listing_num} ''')
        return
    
    if len(invite_message_text) ==  0:
        invite_message_text = """Hi {Candidate_name}, 

    We are interested in your profile for internship at Systemic Altruism. Accept our invite to get shortlisted for this opportunity. 

    Thanks,
    Jack Jay
    Systemic Altruism"""
    
    print('initiating automation')
    # STEP 1 Inviting everyone from access database
    access_database_ids = await get_all_from_access_database(listing_num)
    await send_invite_to_access_database(application_ids=access_database_ids, listing_num=listing_num, invite_message=invite_message_text)
    
    # STEP 2 Send Intro message to everyone who applied
    applicant_database_ids = await get_all_from_applicant_database(listing_num)
    await send_intro_to_applicant_database(ids=applicant_database_ids, listing_num=listing_num, intro_message=intro_message_text)

    # STEP 3 Short list everyone from applicant database
    await shortlist_everyone(ids=applicant_database_ids, listing_num=listing_num)

    # new_ids = applicant_database_ids[:10]
    # print(len(new_ids))
    # await shortlist_everyone(ids=new_ids, listing_num=listing_num)
    
    print('Sleeping for 30 seconds... 💤')
    await asyncio.sleep(30) 
        
    # STEP 4
    # Send assignment to everyone who's shortlisted
    shortlisted_database_ids = await get_all_shortlisted_applicants(listing_num)
    await send_assignment_to_all_shortlisted(ids=shortlisted_database_ids, listing_num=listing_num, assignment=assignment_text)

    if process_text == "offer":
        print('Initiating Hiring Process')
        await hire_shortlisted(ids=shortlisted_database_ids, listing_num=listing_num)
        
    print('DONE ALL')

async def get_all_from_access_database(listing_num: str):
    print("access_database")
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

            # internship_id for jobs too
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
                # print("Success:", response.text)
                # print("Success:", json.load(response.text))
                html_response = json.loads(response.text)['view']
                ids = re.findall(r'class=\"application_id\">(\d+)<\/div>', html_response)
                application_ids = application_ids + ids
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
            if offset > 500:
                break
            offset = offset + 10
            if offset % 50 == 0:
                os.system('cls')
                print('''getting id's from Access Database: [''','# ' * int(offset / 50), '- ' * (10 - int(offset / 50)), ']')                
                # ✅ TODO fetching only 10 candidataes for testing move out all 3 line below this
        # print(application_ids)
        # print(len(application_ids))
            
        print('''successfully got id's of everyone inside Access Database''')
        return application_ids
    except:
        traceback.print_exc()
        print('Breaking while getting candidates ids from Access database')
        return
        
async def send_invite_to_access_database(application_ids:list, listing_num:str, invite_message:str):
    print('sending invite to access database')
    session = requests.Session()
    try:
        if len(application_ids) > 0:
            print('invting... All ids from short listed')
            # The base endpoint for changing the status of applications
            url = 'https://internshala.com/employer/invitation'
            # Convert list of application IDs to a comma-separated string
            application_ids_str = ','.join(application_ids)

            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
                        
                # Correctly formatted data for the POST request body
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

            # Headers for the request
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': payload.content_type,
                'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/invite'
            }

            # Make the POST request with the cookies, headers, and the specified data
            print('Started sending requests')
            response = session.post(url, headers=headers, data=payload)

            # Check the response
            if response.status_code == 200:
                # print("Success:", response.text)
                print("successfully sent invite to everyone in Access Database")
                print('Sleeping for 5 mins... 💤')
                await asyncio.sleep(300)    
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                return False
                    
            # successfully sent invite to everyone in Access Database
            print('''successfully sent invite to everyone in Access Database''')
            return True
    except:
        print('Facing error while sending invite to candidates in Access Database')
        return False

async def get_all_from_applicant_database(listing_num:str):
    print('Getting ids of applicant who applied')
    try:
        session = requests.Session()
        # The endpoint for changing the selecting all applications to get their id and updating cookies
        url = f'https://internshala.com/employer/get_data_for_select_all/{listing_num}'

        with open('internshala_automation.pkl', 'rb') as f:
            loaded_cookies = pickle.load(f)
            for cookie in loaded_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
                    
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

        response = session.post(url, headers=headers, data=data)
        ids = []
        # Check the response
        if response.status_code == 200:
            ids = json.loads(response.text)['applications_id']
        else:
            print('''error while shortlisting "from else"''')
            print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
        # successfully getting Id's of everyone who applied
        print('''successfully getting Id's of everyone who applied''')
        # print(ids)
        # print(len(ids))
        return ids
    except:
        print("error while shortlistng")
 
async def send_intro_to_applicant_database(ids:list, listing_num:str, intro_message:str):
    print('Sending intro to all from applicant database')
    try:
        if len(ids) > 0:
            session = requests.Session()
            if len(intro_message) != 0:
                with open('internshala_automation.pkl', 'rb') as f:
                    loaded_cookies = pickle.load(f)
                    for cookie in loaded_cookies:
                        session.cookies.set(cookie['name'], cookie['value'])
                            
                url = 'https://internshala.com/chat/send_message_from_employer_dashboard'
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
                    print("successfully sent intro message to everybody who applied")
                    print('Sleeping for 5 mins... 💤')
                    await asyncio.sleep(300)
                else:
                    print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    print('error while sending intro message "from else"')
                    return False
                # successfully sent intro message to everybody who applied
                print('''successfully sent intro message to everybody who applied''')
                return True
    except:
        print('error while sending intro message')
        traceback.print_exc()
        return False

async def shortlist_everyone(ids: list, listing_num:str):
    print('Shortlisting everyone')
    try:
        session = requests.Session()
        url = 'https://internshala.com/application/change_status/'
        # Load cookies from the updated file
        with open('internshala_automation.pkl', 'rb') as f:
            loaded_cookies = pickle.load(f)
            for cookie in loaded_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

        # Headers as observed from the actual request
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'internshala.com',
            'Origin':'https://internshala.com',
            'Referer': f'https://internshala.com/employer/applications/{listing_num}/1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
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
            print("Success:")
            # print("Success:", response.json())
        else:
            print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
            print('''error while shortlisting everyone "from else" ''')
            return False
                    
        # short listed everyone from Applications Database (Applicant who applied)
        print('''short listed everyone from Applications Database ''')
        return True
    except:
        print('''error while shortlisting everyone''')
        traceback.print_exc()
        return False

async def get_all_shortlisted_applicants(listing_num: str):
    print('Getting ids of shortlisted applicants')
    try:
        session = requests.Session()
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
            # print(response.text)
            ids = json.loads(response.text)['applications_id']
        else:
            print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
            print(f"error while getitng ids of all shortlisted applicants 'from else' ")
            return False, response.status_code
        
        # print(len(ids))            
        # Successfully getting Id of everyone who's shortlisted
        print('''Successfully getting Id of everyone who's shortlisted''')
        return ids
    except:
        print(f"error while getitng ids of all shortlisted applicants")
        traceback.print_exc()
        return False
        
async def send_assignment_to_all_shortlisted(ids:list, listing_num:str, assignment:str):
    print('sending assignment')
    try:
        session = requests.Session()
        if len(ids)>0:
            url = 'https://internshala.com/employer/assignment_submit'
            # Convert list of application IDs to a comma-separated string
            application_ids_str = ','.join([str(id) for id in ids])
            submission_deadline_date = datetime.now() + timedelta(days=4)
            # Format the date as 'dd MMM' YY' e.g., '29 Mar' 24'
            submission_deadline_str = submission_deadline_date.strftime('%d %b\' %y')

            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
            
            # Correctly formatted data for the POST request body
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
                'Referer':f'https://internshala.com/employer/applications/{listing_num}/1/shortlisted',
                'X-Requested-With':'XMLHttpRequest'
            }

            # Make the POST request with the cookies, headers, and the specified data
            response = session.post(url, headers=headers, data=payload)

            # Check the response
            if response.status_code == 200:
            # print("Success:", response.text)
                print("Assignment sent successfully to all short listed applicants")
                print('Sleeping for 5 mins... 💤')
                await asyncio.sleep(300)
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                print('''Error while sending assignment "from else" ''')
                return False

                # Assignment sent successfully to all short listed applicants
            print(''' Assignment sent successfully to all short listed applicants''')
            return True
    except:
        traceback.print_exc()
        return False
    
async def hire_shortlisted(ids: list, listing_num:str):
    print('Started Hiring shortlisited Candidates')
    try:
        session = requests.Session()
        url = 'https://internshala.com/application/change_status/'
        # Load cookies from the updated file
        with open('internshala_automation.pkl', 'rb') as f:
            loaded_cookies = pickle.load(f)
            for cookie in loaded_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

        headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': f'https://internshala.com/employer/applications/{listing_num}/1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    # Include any other headers observed in the successful request
                }
        data = {
                    'status_change_referral': 'bulk_operator',
                    'change_status_source': 'new_dashboard',
                    'old_status': 'open',
                    'status': 'hired',
                    # The 'id[]' part will be handled separately to ensure proper formatting
                }
        id_payload = '&'.join(f'id[]={id_val}' for id_val in ids)
        data_encoded = '&'.join([f'{key}={value}' for key, value in data.items()])
        full_payload = f'{data_encoded}&{id_payload}'

        # Making the POST request with the custom payload
        response = session.post(url, headers=headers, data=full_payload)
        if response.status_code == 200:
            print("Success")
            # print("Success:", response.json())
        else:
            print('error while hiring shortlisted users "from else" ')
            print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            return False
        print('Succsfully hired everybody who was in shortlisted database')
        return True
    
    except:
        print('error while hiring shortlisted users')
        traceback.print_exc()
        return False
    
async def send_message_using_id(ids:list, message:str, listing_num:str):
    print('''sending messages using id's''')
    try:
        session = requests.Session()
        if len(message) != 0:
                       
            with open('internshala_automation.pkl', 'rb') as f:
                loaded_cookies = pickle.load(f)
                for cookie in loaded_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])
            
            url = 'https://internshala.com/chat/send_message_from_employer_dashboard'
            # application_ids_str = ','.join(ids)
            application_ids_str = ','.join([str(id) for id in ids])

            payload = MultipartEncoder(
                fields={
                    'application_ids': application_ids_str,  # Assuming the API can handle multiple IDs in this field
                    'referral': 'bulk',
                    'message': f'{message}',
                    'internship_id': f'{listing_num}',
                    'auto_populated_attachments': '[]'
                    }
                )
                
                # payload

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
                print("Success")
                # print("Success:", response.text)
                # with open('internshala_automation_updated_1.pkl', 'wb') as f:
                #     pickle.dump(session.cookies, f)

                print('Sleeping for 5 mins... 💤')
                await asyncio.sleep(300)
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                traceback.print_exc()
                return False
            return True
    except:
        print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
        traceback.print_exc()
        return False

async def run_1(listing_num):
    # task = asyncio.create_task(send_message(['194347871'], "This is test intro to mk", listing_num="2456074"))
    # access_database = asyncio.run(get_all_from_access_database(listing_num))
    # applicant_database = asyncio.run(get_all_from_applicant_database(listing_num))
    # shortlisted_database = asyncio.run(get_all_shortlisted_applicants(listing_num))
    access_database = await get_all_from_access_database(listing_num)
    applicant_database = await get_all_from_applicant_database(listing_num)
    shortlisted_database = await get_all_shortlisted_applicants(listing_num)
    
    print('access database: ', len(access_database))
    print('applicant database: ', len(applicant_database))
    print('shortlisted database: ', len(shortlisted_database))

if __name__ == "__main__":
    print('Here i come!')
    if len(sys.argv) != 2:
        print("need a listing number")
        sys.exit(1)
        
    listing_number = str(sys.argv[1])
    asyncio.run(automate(listing_num=listing_number))
    # asyncio.run(run_1(listing_number))
    
    