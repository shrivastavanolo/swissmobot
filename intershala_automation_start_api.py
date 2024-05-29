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

# listing_num = "2462410"
async def automate(listing_num:str):
    intro_message = ""
    invite_message = ""
    assignment = ""
    process = ''
    
    #Finding row with listing, getting assignment, process, if intro , if invite
    current_listing = query_get_one('''SELECT * FROM projects WHERE listing = ?''', [listing_num])
    # print(current_listing)
    # return
    
    if current_listing:
        print(current_listing['name'])
        if current_listing['assignment']:
            assignment = current_listing['assignment']
            print(assignment)
        if current_listing['intro']:
            intro_message = current_listing['intro']
            print(intro_message)
        if current_listing['invite']:
            invite_message = current_listing['invite']
            print(invite_message)
        if current_listing['process']:
            process = current_listing['process']
            print(process)
    else:
        print(f'''couldn't find project with listing number: {listing_num} ''')
        return
    
    if len(invite_message) ==  0:
        invite_message = """Hi {Candidate_name}, 

    We are interested in your profile for internship at Systemic Altruism. Accept our invite to get shortlisted for this opportunity. 

    Thanks,
    Jack Jay
    Systemic Altruism"""
    try:
        # ## Step 1 to invite everyone from internshala database
        # # print('Access Database...')
        # '''time.sleep(1)
        # try:
        #     application_ids = []
        #     offset = 0
        #     while True:
        #         session = requests.Session()
        #         # URL
        #         # The base endpoint for changing the status of applications
        #         url = 'https://internshala.com/employer/paginated_invitations'
        #         # Load cookies from the updated file
        #         with open('internshala_automation.pkl', 'rb') as f:
        #             loaded_cookies = pickle.load(f)
        #             for cookie in loaded_cookies:
        #                 session.cookies.set(cookie['name'], cookie['value'])
                        
        #         # Headers for the request
        #         headers = {
        #             'Accept': '*/*',
        #             'Accept-Encoding': 'gzip, deflate, br, zstd',
        #             'Accept-Language': 'en-US,en;q=0.9',
        #             'Connection': 'keep-alive',
        #             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #         }

        #         # internship_id for jobs too
        #         # Correctly formatted data for the POST request body
        #         data = {
        #             "internship_id": f"{listing_num}",
        #             "offset": f"{offset}"
        #         }

        #         # Make the POST request with the cookies, headers, and the specified data
        #         response = session.post(url, headers=headers, data=data)

        #         # Check the response
        #         ids = []
        #         if response.status_code == 200:
        #             # print("Success:", response.text)
        #             # print("Success:", json.load(response.text))
        #             html_response = json.loads(response.text)['view']
        #             ids = re.findall(r'class=\"application_id\">(\d+)<\/div>', html_response)
        #             application_ids = application_ids + ids

        #         else:
        #             print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
        #         if offset > 500:
        #             break
        #         offset = offset + 10
        #         if offset % 50 == 0:
        #             os.system('cls')
        #             print('processing: [','# ' * int(offset / 50), '- ' * (10 - int(offset / 50)), ']')                

        #         # successfully got id's of everyone inside Access Database
        #         # time.sleep(1)'''
                        
        #     # print('''successfully got id's of everyone inside Access Database''')
        #     # print(application_ids)
        #     # return
        #     '''if len(application_ids) > 0:
        #         print('invting... All ids from short listed')
        #         #URL
        #         # The base endpoint for changing the status of applications
        #         url = 'https://internshala.com/employer/invitation'
        #         # Convert list of application IDs to a comma-separated string
        #         application_ids_str = ','.join(application_ids)

        #         with open('internshala_automation.pkl', 'rb') as f:
        #             loaded_cookies = pickle.load(f)
        #             for cookie in loaded_cookies:
        #                 session.cookies.set(cookie['name'], cookie['value'])
                        
        #         # Correctly formatted data for the POST request body
        #         payload = MultipartEncoder(
        #             fields={
        #                 'application_ids': application_ids_str,
        #                 'referral': 'invitation',
        #                 'message': f'{invite_message}',
        #                 'internship_id': f'{listing_num}', ## change
        #                 'auto_populated_attachments': '[]',
        #                 'action': 'invite',
        #                 'recommend_ids': application_ids_str,
        #                 'page_type': 'application_list_view',
        #                 'to_invite_top_applicants': 'false'
        #             }
        #         )

        #         # Headers for the request
        #         headers = {
        #             'Accept': '*/*',
        #             'Accept-Encoding': 'gzip, deflate, br, zstd',
        #             'Accept-Language': 'en-US,en;q=0.9',
        #             'Connection': 'keep-alive',
        #             'Content-Type': payload.content_type,
        #             'Referer': f'https://internshala.com/employer/applications/{listing_num}/1/invite'
        #         }

        #         # Make the POST request with the cookies, headers, and the specified data
        #         response = session.post(url, headers=headers, data=payload)

        #         # Check the response
        #         if response.status_code == 200:
        #             # print("Success:", response.text)
        #             print("successfully sent invite to everyone in Access Database")
        #             print('Sleeping for 5 mins... 💤')
        #             await asyncio.sleep(300)
        #             # with open('internshala_automation_updated_1.pkl', 'wb') as f:
        #             #     pickle.dump(session.cookies, f)
        #         else:
        #             print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
        #         # successfully sent invite to everyone in Access Database'''
        #         # print('''successfully sent invite to everyone in Access Database''')
        #         # time.sleep(1)
        # '''except:
        #     traceback.print_exc()
        #     print("e")
        #     pass'''
        
        # same process for assignment and offerletter
        print('ASsignment')
        try:
            session = requests.Session()
            #URL
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
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                        
            time.sleep(1)
            # successfully getting Id's of everyone who applied
            print('''successfully getting Id's of everyone who applied''')
            
            ## to  send message
            if len(ids)>0:
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

                    time.sleep(1)
                    # successfully sent intro message to everybody who applied
                    print('''successfully sent intro message to everybody who applied''')
        except:
            traceback.print_exc()
            pass
        
        # short listing everyone from Applications Database (Applicant who applied)
        try:
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
            # 'Cookie': 'your_cookie_string_here',  # Ensure this is updated with your actual cookie string
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

            # FIND ME shortlist request
            # Making the POST request with the custom payload
            response = session.post(url, headers=headers, data=full_payload)

            if response.status_code == 200:
                print("Success:", response.json())
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                    
            # short listed everyone from Applications Database (Applicant who applied)
            print('''short listed everyone from Applications Database (Applicant who applied)''')
            time.sleep(1)
        except:
            print('issue while shortlisting people from Applicant database ☠')
            traceback.print_exc()
            pass
        
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
                print(response.text)
                ids = json.loads(response.text)['applications_id']
            else:
                print(f"Failed to update status: HTTP {response.status_code}, Response: {response.text}")
                
            # Successfully getting Id of everyone who's shortlisted
            print('''Successfully getting Id of everyone who's shortlisted''')
            time.sleep(1)
            # print(ids)
                
            if len(ids)>0:
                # The base endpoint for sending assignemnt
                url = 'https://internshala.com/employer/assignment_submit'
                # application_ids = ['192355094', '192353578']

                # Convert list of application IDs to a comma-separated string
                application_ids_str = ','.join([str(id) for id in ids])
                # Headers for the request
                submission_deadline_date = datetime.now() + timedelta(days=4)

                # Format the date as 'dd MMM' YY' e.g., '29 Mar' 24'
                submission_deadline_str = submission_deadline_date.strftime('%d %b\' %y')

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

                # Assignment sent successfully to all short listed applicants
                print('''# Assignment sent successfully to all short listed applicants''')
                time.sleep(1)
                        
        except:
            traceback.print_exc()
            pass
                       
    except:
        print("here")
        traceback.print_exc()
        pass
    print('DONE ALL')
    
async def get_all_shortlisted_applicants(listing_num: str):
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
                
    # Successfully getting Id of everyone who's shortlisted
    time.sleep(1)
    return ids

async def send_message_using_id(ids:list, message:str, listing_num:str):

    session = requests.Session()
    if len(message) != 0:
        # https://internshala.com/employer/get_data_for_select_all/2462410
        
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

async def run_1(ids):
    # task = asyncio.create_task(send_message(['194347871'], "This is test intro to mk", listing_num="2456074"))
    # await task
    for i in range(10):
        print(ids[i])
    pass

# 2462410
if __name__ == "__main__":
    print('Here i come!')
    if len(sys.argv) != 2:
        # print("Usage: python heart_research.py <folder_path>")
        print("need a listing number")
        sys.exit(1)
        
    listing_number = str(sys.argv[1])
    asyncio.run(automate(listing_num=listing_number))
    
    