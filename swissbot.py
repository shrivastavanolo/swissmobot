import os
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from telegram._files.document import Document
import logging
import json
import re
import traceback
import csv
from datetime import datetime
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai
from queries import cx
from queries import add_project, remove_project, search_project
from queries import add_leader, search_leader, get_leaders, update_leader
from queries import add_candidate, search_candidate, get_candidates, update_candidate, get_candidate_count
import form
import sys
import database
######### To do: Set your email at line 870 in function 'send_email' ############

# APIs and tokens
unique_id_recruiter = 'NA'
openai.api_key = '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'
openai.api_base = 'https://api.perplexity.ai'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#change this token to change bot
TOKEN = '7098210763:AAGcqaIofG1mE_KtZkEVGroOVJPK4Tnzoew'

dct_users = {}

#### /start for new session
#### /start xjfysbrv_<project> for new leaders
#### /start dewdrop_<project> for assignment candidates
#### /start rcbwin_<project> for offerletter candidates

#start function 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args: list = context.args
    print(args)
    if not args:
      #new session start here
      await update.message.reply_text(
      "Welcome to Swissmote Bot, exclusively for Persist Venture! \n\n"
      "I'm here to streamline your workflow with specialized functions:\n\n"
      "For a simplified recruiting process(Assignment or Offer Letter), including automated sending assignments, message, invite, shortlist and hiring on Internshala, use the command: /automate_internshala. This will ensure a fully automated process, eliminating the need for manual intervention.\n\n"
      "Connect with our Vision:  https://www.youtube.com/watch?v=itGNk0wellQ")
      
      await automate_internshala(update,context)
      return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    name = update.effective_chat.first_name 
    project: str = args[0]
    if project.startswith("xjfysbrv_"):
      #new Leader enters here using /start xjfysbrv_<project>
      project = project.split("_")[1]
      if search_project(project) is None:
        await update.message.reply_text("Invalid argument!")
        return
      # leader = add_leader(chat_id, project)
      leader = add_leader(user_id, project)
      if leader:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot." + "\n" + \
        "Here, you'll receive all assignment submissions and daily updates. 📬" + "\n" + \
        "Plus, you can mass messages directly to everyone—just send it to me, and I will personally send this message to everyone 📢" + "\n" + \
        "Let’s dive in! 💪"
        await update.message.reply_text(message, reply_markup=leader_deafult_keyboard)
        return
      #if leader already exists for the project
      elif not leader:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot," + "\n" + \
        "you are already a leader for this project."
        await update.message.reply_text(message, reply_markup=leader_deafult_keyboard)
        return
    print(project.split("_")[1])
    #if project doesnt exist
    project_details = search_project(project.split("_")[1])
    if project_details is None:
      await update.message.reply_text("Invalid argument!")
      return
    
    # candidate = add_candidate(chat_id, project, datetime.now().timestamp())
    # print('CANDY 🍬')
    # print(user_id, project, datetime.now().timestamp())

    candidate = add_candidate(user_id, project.split("_")[1], int(datetime.now().timestamp()))
    
    #if candidate already belongs to another project (can't have 2 projects at the same time)
    if not candidate:
      message = f"🎉 Hello {name}! Welcome to SwissmoteBot," + "\n" + \
      "you are already a candidate for another project. Use /instructions to know more."
      return
    message = "🎉 Welcome to SwissmoteBot! I'm a bot designed by Systemic Altruism to keep you updated on the Hiring Process🚀" + "\n" + \
      "Congratulations on being shortlisted! 🌟 To be hired with a PPO, here’s what you need to do:" + "\n" + \
      "1. 📈 Share your daily updates and progress with me." + "\n" + \
      "2. 📤 Submit your assignments here when ready." + "\n" + \
      "The main thing we want to see in completing your assignment is not only your ability to learn something entirely new and push through to complete the task, but also your speed in doing so." + "\n" + \
      "If you want this job, you should go and try and speed run crushing this assignment, If it takes you a few days give us a daily update on where you've made progress so we can assess your ablilty to learn quickly." + "\n" + \
      "Check /instructions to understand the process better. Let’s get started! 💪." + "\n" + \
      "Connect with our Vision:  https://www.youtube.com/watch?v=itGNk0wellQ"
    
    if project.startswith("dewdrop_"):
      #assignment candidate
      await update.message.reply_text(message)
      await update.message.reply_text(project_details["assignment"], reply_markup=candidate_deafult_keyboard)
    
    elif project.startswith("rcbwin_"):
      #offer letter candidate
      await context.bot.send_message(chat_id=chat_id, text="⏳ Please wait while we process your offer letter... 📝")
      try:
        print('start')
        full_name=f"{update.effective_chat.first_name } {update.effective_chat.last_name}"
        
        project_split = project.split('_')[1]
        # form.pdf_top(full_name,"Persist Ventures",f"{project_split} intern",project_details["assignment"],f"https://telegram.me/heytohbot?start=rcbwin_{dct_users[user_id]['project_name_']}",f"{full_name}_{project_split}_offerletter.pdf")
        
        await update.message.reply_text(project_details["assignment"], reply_markup=candidate_deafult_keyboard)
        try:
          print('form')
          form.pdf_top(name=full_name,
                      filepath=f"offer_letters/{full_name}_{project_split}_offerletter.pdf"
                    )
        except:
          print('really bro')
          
        await context.bot.send_document(chat_id=chat_id, document=open(f"offer_letters/{full_name}_{project_split}_offerletter.pdf","rb"))
      except Exception as e:
        print(e)

        
    #sends a candidate count to the project leader whenever new candidate joins  
    candidate_count = get_candidate_count(project)
    message = "🌟 New Applicant! 🌟" + "\n" + \
    f"{name} has just joined SwissmoteBot for the {project} Assignment" + "\n" + \
    "We gave them an warm welcome and succesfully Sent Assignment!" + "\n" + \
    f"Total Applicants: {candidate_count['count']}"
    leaders = get_leaders(project)
    for leader in leaders:
      if not leader["join_message"]:
        join_message = await context.bot.send_message(chat_id=leader["chat_id"], text=message)
      else:
        await context.bot.delete_message(chat_id=leader["chat_id"], message_id=leader["join_message"])
        join_message = await context.bot.send_message(chat_id=leader["chat_id"], text=message)
      update_leader(leader["chat_id"], join_message.message_id)      
      return

#gets listing of internships from internshala
async def choose_listing_automate(update: Update, context: ContextTypes.DEFAULT_TYPE,flag:int, page_num, emp_type ) -> None:  
    global dct_users
    user_id = update.effective_user.id
    
    await update.callback_query.edit_message_text(text="🔄 Fetching The Latest Listing From Internshala.")
    dct_users[user_id]['emp_type'] = emp_type
    keyboard = [
        [InlineKeyboardButton("Next >>", callback_data=f'next_{str(int(page_num) + 1)}_{emp_type}_{user_id}'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    success = await run_async_process_mk(['get_listing_details_api.py', str(page_num), emp_type])
    if not success:
        await context.bot.send_message(chat_id=int(user_id), text=f"⚠️ Oops! We Encountered An Issue Fetching The Listing. We Informed The Dev Team. 🛠️")
        send_email("Fail","Fail in get listing")
        return
    else:
        await update.callback_query.edit_message_text(text=f"Page: {page_num} 📄" )
        # await context.bot.send_message(chat_id=int(user_id), text=f"Success! ✅")
    
    if emp_type == 'internship':       
        file_path = "internship_details.txt"
        
    elif emp_type == 'job' :
        file_path = 'job_details.txt'
        
    message = ""
    active_projects = await database.get_all_active_projects()
    active_listing = []
    for project in active_projects:
        active_listing.append(str(project[0]))
    
    with open(file_path, 'r') as file:
      for line in file:
        split_line = line.split('___')
        count = split_line[0]
        name = split_line[1]
        package = split_line[3]         

        if 'None' in package:
          message = message + f"{count}. {name}\n\n"
        else:
          if split_line[2] in active_listing:
            print('ACTIVE ' , '🟢'*7)
            message = message + f"{count}. {name} 🟢 \n{package}\n"
            active_listing.remove(split_line[2])
          else:
            message = message + f"{count}. {name} \n{package}\n"
                    
    if message == "":
      await update.callback_query.edit_message_text(text="That's All ✅", parse_mode='Markdown')
    else:
      add = '🟢 represent an Active project on a Listing \nuse /all to get list of all active projects \n\n'
      add += message
      if flag == 0:
        await context.bot.send_message(chat_id=int(user_id), text=add, parse_mode='Markdown', reply_markup=reply_markup)
        return
      elif flag==1:
        message += "🔢 Enter the Listing Number, Please!"
        await context.bot.send_message(chat_id=int(user_id), text=add, parse_mode='Markdown', reply_markup=reply_markup)
        await listing(update, context)
    
#Automate internshala command starts here
async def automate_internshala(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  if not search_leader(chat_id=user_id):
    await update.message.reply_text('Only leaders can use this command')
    return
  asyncio.create_task(background_automate_internshala(update, context))
  
async def automate_internshala_gift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  asyncio.create_task(background_automate_internshala(update, context))
    
#bg automation
async def background_automate_internshala(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    global dct_users
    user_id = update.effective_user.id
        
    await update.message.reply_text('Welcome to Fully Automated Funnel 🚀')
    dct_users[user_id] = {'project_name': False, 'listing': False, 'assignment': False, 'invite_message': False, 'intro_message': False, 'followup_2': False, 'followup_4': False, 'assignment_process': False, 'listing_num' : 0, 'invite_message_': False, 'intro_message_': False, 'reviewer':False}
    keyboard = [
        [InlineKeyboardButton("Create Listing", callback_data=f'create_{user_id}')],
        [InlineKeyboardButton("Choose Listing", callback_data=f'choose_{user_id}')],
        [InlineKeyboardButton("View Listing", callback_data=f'view_{user_id}')],
    ]
    #admin keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("""
                                    Admin Dashboard 📃📊

                                    """, reply_markup=reply_markup)


def save_details_in_file(listing, project_name, process = 'NA', invite = 'NA', intro = "NA", assignment = 'NA', followup2 = 'NA', followup4 = 'NA', status = 'Inactive', date = datetime.now().strftime("%Y-%m-%d"), followup2status = 'Inactive', followup4status = 'Inactive', file_path = 'listings\\intern_listing.csv'):
    # Check if the csv file exists, if not, create it and add headers
    try:
        try:
            with open(file_path, 'x', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # messages, intern status, date, day2 status, day3 status, day4 status, leader_id , process_type
                writer.writerow(['listing', 'projectname', 'process', 'invite', 'intro', 'assignment', 'followup2', 'followup4', 'status', 'date', 'followup2status', 'followup4status'])
        except FileExistsError:
            pass 

        # Append the data to the CSV
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([listing, project_name, process, invite, intro, assignment, followup2, followup4, status, date, followup2status, followup4status])
    except:
        traceback.print_exc()
        pass


async def update_details_in_file(listing, project_name = None, process=None, invite=None, assignment=None, followup2=None, followup4=None, status=None, date = None, followup2status=None, followup4status=None, file_path = 'listings\\intern_listing.csv'):
    try:
        data = []
        with open(file_path, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row['listing'] == str(listing):
                    if process is not None:
                        row['process'] = str(process)
                    if invite is not None:
                        row['invite'] = str(invite)
                    if assignment is not None:
                        row['assignment'] = str(assignment)
                    if followup2 is not None:
                        row['followup2'] = str(followup2)
                    if followup4 is not None:
                        row['followup4'] = str(followup4)
                    if status is not None:
                        row['status'] = str(status)
                    if date is not None:
                        row['date'] = date
                    if project_name is not None:
                        row['projectname'] = project_name
                    if followup2status is not None:
                        row['followup2status'] = str(followup2status)
                    if followup4status is not None:
                        row['followup4status'] = str(followup4status)
                data.append(row)
        with open(file_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['listing','projectname', 'process', 'invite', 'intro', 'assignment', 'followup2', 'followup4', 'status', 'date', 'followup2status', 'followup4status']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        traceback.print_exc()
    

async def project_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = True
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    await context.bot.send_message(chat_id=int(user_id), text="Enter Project Name:")


async def listing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = True
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    await context.bot.send_message(chat_id=int(user_id), text="🔢 Enter the Listing Number, Please!")


async def give_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = True
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    if dct_users[user_id]['assignment_process'] == True:
# A Swissmote link : https://telegram.me/heytohbot?start=dewdrop_{dct_users[user_id]['project_name_']}
        message= f"""
📝 Assignment Submission
Please provide your assignment. Make sure it includes:

A link to the assignment 🖇️
A Loom video 📹
A Swissmote link : https://t.me/swissmotepvbot?start=dewdrop_{dct_users[user_id]['project_name_']}

Suggestions? Use /suggestion."""
        await context.bot.send_message(chat_id=int(user_id), text=message)
    else:
# Keep Swissmote.0 link : https://telegram.me/heytohbot?start=rcbwin_{dct_users[user_id]['project_name_']}
        message= f"""
📝 Hired Message
Please enter the hired message as per the offer letter process.

Keep Swissmote.0 link : https://t.me/swissmotepvbot?start=rcbwin_{dct_users[user_id]['project_name_']}

Suggestions? Use /suggestion."""
        await context.bot.send_message(chat_id=int(user_id), text=message)
    # 5233340898


async def invite_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = True
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    # if dct_users[user_id]['assignment_process'] == True:
    await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Invitation Message*
Enter an invite message to be sent to the Internshala provided database.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    

async def intro_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = True
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    if dct_users[user_id]['assignment_process'] == True:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Introduction Message*
Enter an intro message for candidates who have applied for this job.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Introduction Message*
Enter an intro message for candidates who have applied for this job.

To *skip*, use */skip*. For *suggestions*, use */suggestion*.""", parse_mode='Markdown')


async def followup_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = True
    dct_users[user_id]['followup_4'] = False
    dct_users[user_id]['reviewer'] = False
    if dct_users[user_id]['assignment_process'] == True:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 2*
Enter the follow-up message for Day 2 after sending the assignment.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    
    else:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 2*
Enter the follow-up message for Day 2.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    
    
async def followup_4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    dct_users[user_id]['project_name'] = False
    dct_users[user_id]['listing'] = False
    dct_users[user_id]['assignment'] = False
    dct_users[user_id]['invite_message'] = False
    dct_users[user_id]['intro_message'] = False
    dct_users[user_id]['followup_2'] = False
    dct_users[user_id]['followup_4'] = True
    dct_users[user_id]['reviewer'] = False
    if dct_users[user_id]['assignment_process'] == True:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 4*
Enter the follow-up message for Day 4 after sending the assignment.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    
    else:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 4*
Enter the follow-up message for Day 4.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
    

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    ## give message if u want
    try:
        # dct_users[user_id] = {'listing': False, 'assignment': False, 'invite_message': False, 'intro_message': False, 'followup_2': False, 'followup_4': False}
        if dct_users[user_id]['invite_message'] == True:
            try:
                dct_users[user_id]['invite_message'] = False
                dct_users[user_id]['intro_message'] = True
                if dct_users[user_id]['assignment_process'] == True:
                    await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Introduction Message*
Enter an intro message for candidates who have applied for this job.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
                else:
                    await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Introduction Message*
Enter an intro message for candidates who have applied for this job.

To *skip*, use */skip*. For *suggestions*, use */suggestion*.""", parse_mode='Markdown')
            except:
                traceback.print_exc()
        elif dct_users[user_id]['intro_message'] == True:

            try:
                dct_users[user_id]['intro_message'] = False
                dct_users[user_id]['assignment'] = True
                if dct_users[user_id]['assignment_process'] == True:
# - Swissmote2.0 link : https://telegram.me/heytohbot?start=dewdrop_{dct_users[user_id]['project_name_']}
                  await context.bot.send_message(chat_id=int(user_id), text=f"""
📝 *Assignment Submission*
Please provide your assignment. Make sure it includes:

- link to the assignment 🖇️
- Loom video 📹
- Swissmote2.0 link : https://t.me/swissmotepvbot?start=dewdrop_{dct_users[user_id]['project_name_']}

*Suggestions?* Use /suggestion."""
, parse_mode='Markdown')
                else:
# Keep Swissmote.0 link : https://telegram.me/heytohbot?start=rcbwin_{dct_users[user_id]['project_name_']}
                   await context.bot.send_message(chat_id=int(user_id), text=f"""
📝 *Hired Message*
Please enter the hired message as per the offer letter process.

Keep Swissmote.0 link : https://t.me/swissmotepvbot?start=rcbwin_{dct_users[user_id]['project_name_']}

*Suggestions?* Use */suggestion*.""", parse_mode='Markdown')            
                  
            except:
                traceback.print_exc()
        
        elif dct_users[user_id]['followup_2'] == True:
            dct_users[user_id]['followup_2'] = False
            dct_users[user_id]['followup_4'] = True
            if dct_users[user_id]['assignment_process'] == True:
                await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 4*
Enter the follow-up message for Day 4 after sending the assignment.
To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')           
            else:
                await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Follow-Up for Day 4*
Enter the follow-up message for Day 4.

To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')          
        elif dct_users[user_id]['followup_4'] == True:
            dct_users[user_id]['followup_4'] = False
            # await context.bot.send_message(chat_id=int(user_id), text=f"""Leader need to join from this link: https://telegram.me/heytohbot?start=xjfysbrv_{dct_users[user_id]['project_name_']}""")
            await context.bot.send_message(chat_id=int(user_id), text=f"""Leader need to join from this link: https://t.me/swissmotepvbot?start=xjfysbrv_{dct_users[user_id]['project_name_']}""")
          
            asyncio.create_task(execute_internshala_automation(update, context))
    except:
        pass


async def suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_chat.id
    ## give message if u want
    try:
        # dct_users[user_id] = {'listing': False, 'assignment': False, 'invite_message': False, 'intro_message': False, 'followup_2': False, 'followup_4': False}
        if dct_users[user_id]['assignment'] == True:
            try:
                if dct_users[user_id]['assignment_process'] == True:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Assignment Template*
```
Hey {{firstName}}

Wanted to Invite you to join our Giphy/Meme creation internship:

YOYOYO,

Welcome to the Giphy Internship, have a short task made a video here for you

This explains it!
https://www.loom.com/share/ad2ebf86e18d460c9c901a0d66f132f3

Giphy Account Login:
Username: contact@jackjay.io
Pass: pronoia1!

Link To Make Gifs From:
https://photos.app.goo.gl/VDhDWusSEpLiEPaa8

Thanks,
Jack Jay
https://Instagram.com/web3wizard
```
""", parse_mode='Markdown')
                else:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Offer Letter Template*
```
Hey (FirstName), we saw your profile and think you would be a great asset to our team. Here is an offer letter for your internship with us. 

With Persistence you will lead from this internship, into a full time offer and we’ve laid out a base track and salary over time via the long term partnership we are looking to make with the interns who persist through our internship test :) 

You’ll find more details in the offer letter! 

[PUT SIGN WELL OFFER LETTER LINK HERE]

Excited about you being a part of the company,

Thanks,
Jack Jay
Founder Persist Ventures & Systemic Altruism

Follow Us Here:

https://twitter.com/systemicalt
https://twitter.com/persistventures
https://instagram.com/persistventures
https://www.linkedin.com/company/persist-ventures

And I often like and retweet, and post useful stuff here too
https://twitter.com/jackjayio
https://instagram.com/web3wizard
https://www.linkedin.com/in/jack-jay-jackson-jesionowski/

“Look, if you had one shot, or one opportunity. To seize everything you ever wanted in one moment. Would you capture it or just let it slip?”
― Eminem
```
""", parse_mode='Markdown')
            except:
                traceback.print_exc()
        if dct_users[user_id]['invite_message'] == True:
            try:
                if dct_users[user_id]['assignment_process'] == True:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Invite Message Template*
```
Hey!

Want to invite you to apply to our role. We are building an amazing ecosystem of top talent.

We really do not care about experience, resume, etc, just if you can show us awesome skills, and persistence then you have a place here.

Thanks,

Jack Jay Founder Systemic Altruism & Persist Ventures
[Https://instagram.com/web3wizard](https://instagram.com/web3wizard)
[https://Twitter.com/JackJayio](https://twitter.com/JackJayio)
https://www.linkedin.com/in/jack-jay-jackson-jesionowski/
```
""", parse_mode='Markdown')
                else:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Invite Message Template*
```
Hey!

Want to invite you to apply to our role. We are building an amazing ecosystem of top talent.

We really do not care about experience, resume, etc, just if you can show us awesome skills, and persistence then you have a place here.

Thanks,

Jack Jay Founder Systemic Altruism & Persist Ventures
[Https://instagram.com/web3wizard](https://instagram.com/web3wizard)
[https://Twitter.com/JackJayio](https://twitter.com/JackJayio)
https://www.linkedin.com/in/jack-jay-jackson-jesionowski/
```
""", parse_mode='Markdown')
            except:
                traceback.print_exc()
        elif dct_users[user_id]['intro_message'] == True:
            try:
                if dct_users[user_id]['assignment_process'] == True:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Intro Message Template*
It can be an Introduction message if you would like to say anything else /skip.
""", parse_mode='Markdown')
                else:
                    await context.bot.send_message(chat_id=int(user_id), text="""👥 *Intro Message Template*
It can be an Introduction message if you would like to say anything else /skip.
""", parse_mode='Markdown')
            except:
                traceback.print_exc()
        elif dct_users[user_id]['followup_2'] == True:
            if dct_users[user_id]['assignment_process'] == True:
                await context.bot.send_message(chat_id=int(user_id), text="""👥 *Follow up Template*
```
Hey hope thing have been well, I am bulk sending a follow-up message just because after checking chat messages I saw some of you didnt submit the assignment directly, but instead just pasted it in the chat. (https://chat.whatsapp.com/CJ2a8OPNCWZFgc7TtNYaD8)

(There are too many auto-replies in the chat for me to account for which is why I made this group chat, where I asked people to send the video demo)

THE MAIN THING PEOPLE DID WRONG IS HARD CODING, RATHER THAN CODING ANY FUNCTIONS YOU SHOULD BE ASKING CHATGPT TO WRITE THE CODE BASED ON ITS UNDERSTANDING OF THE TASK.

By the way theres a video for the assignment if you wanted a clearer guide.
https://www.loom.com/share/4af8cb1564974b21a3893080c088d836

We do have a 3 LAKH bonus prize if anyone completes all 7 sample tests as shown here, with quicker speed than their demo's (they didnt have GPT3.5 at the time) on top of the 30LPA+ Yearly Position

I also did a deeper dive into the future of the software we are building you can see here if you want to fully wrap your head around what that job will look like after:
https://www.loom.com/share/f2f34d18239043a4bb9503d9cf43ef36

Then, here's a video that we had as a team meeting with some new recruits (even more insights and talk about the future of what we are building and releasing)
https://drive.google.com/file/d/1TYsp8rfZkUptAnDSSWVRlyx74oRE6Hb9/view?usp=sharing

And lastly, a hype launch short video for the company:
https://www.youtube.com/shorts/vjrAwG73PHk

Hope you guys are as excited about the future of Ai as I am,
Jack Jay CEO Persist Ventures / Workplete
```
""", parse_mode='Markdown')
            else:
                await context.bot.send_message(chat_id=int(user_id), text="""👥 *Follow up Template*
```
ONE FINAL THING.....

I was talking with the Founder's of Mahatma Education Society about the education system. As they are literally based on Mahatama Ghandi who was taught with the hands on, applied skillset approach of hands on learning, they loved the idea of doing a fully applied course...

We did polls recently within our company and found students sometimes learned MORE applicable knowledge in their month of interning than the year of school which does theory and rote memorization. Being from the United States, this method of real learning is called Monetsorri and has consistently raised elite leaders such as Jeff Bezos who founded Amazon.

As someone who personally built a business while skipping class, I decided I should make my dream school become a reality for others younger than me.

And here it is,
https://appliedpillai.com/

Basically it works is like a year long hackathon, you learn by building. This builds real skills, a real portfolio, and we expect billionaire company founders to be trained here.

We have a large job network already, an Ai auto job application bot to apply to hundreds, and some partnerships with startup accelerators who may just invest in these projects rather than you going to a job once you finish.

We are recruiting the best of the best for THIS SCHOOL YEAR

Apply if this sounds like something you can do, if the tuition fees are any higher than your current school, our company will provide a scholarship for you.

Here's the link:
https://AppliedPillai.com
```
""", parse_mode='Markdown')
        elif dct_users[user_id]['followup_4'] == True:
            if dct_users[user_id]['assignment_process'] == True:
                await context.bot.send_message(chat_id=int(user_id), text="""👥 *Inspirational Quotes*
```
"Persistence is the twin sister of excellence. One is a matter of quality; the other, a matter of time." —Marabel Morgan

"Success seems to be connected with action. Successful people keep moving. They make mistakes, but they don't quit." —Conrad Hilton

"You never know what's around the corner. It could be everything. Or it could be nothing. You keep putting one foot in front of the other, and then one day you look back and you've climbed a mountain." —Tom Hiddleston

"Success isn't always about greatness. It's about consistency. Consistent hard work leads to success. Greatness will come." —Dwayne Johnson

"Character cannot be developed in ease and quiet. Only through experience of trial and suffering can the soul be strengthened, vision cleared, ambition inspired and success achieved." —Helen Keller
```
""", parse_mode='Markdown')
            else:
                await context.bot.send_message(chat_id=int(user_id), text="""👥 *Inspirational Quotes*
```
"Persistence is the twin sister of excellence. One is a matter of quality; the other, a matter of time." —Marabel Morgan

"Success seems to be connected with action. Successful people keep moving. They make mistakes, but they don't quit." —Conrad Hilton

"You never know what's around the corner. It could be everything. Or it could be nothing. You keep putting one foot in front of the other, and then one day you look back and you've climbed a mountain." —Tom Hiddleston

"Success isn't always about greatness. It's about consistency. Consistent hard work leads to success. Greatness will come." —Dwayne Johnson

"Character cannot be developed in ease and quiet. Only through experience of trial and suffering can the soul be strengthened, vision cleared, ambition inspired and success achieved." —Helen Keller
```
""", parse_mode='Markdown')
    except:
        pass


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(background_handle_name(update, context))

#function to handle all messages that arent with a command or conversation
async def background_handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    global unique_id_recruiter
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_chat.first_name
    message = update.message.text
    print(message)
    print(dct_users)
    try:
        if dct_users[user_id].get('announcement',0)!=0:
          asyncio.create_task(send_announce(update, context,dct_users[user_id].get('announcement' )))

        elif dct_users[user_id]['project_name'] == True:
            sanitized_message = re.sub(r'\W+', '', message)
            dct_users[user_id]['project_name_'] = sanitized_message
            dct_users[user_id]['project_name'] = False
            keyboard = [
                [InlineKeyboardButton("Assignment", callback_data=f'assignment_{user_id}'),
                InlineKeyboardButton("Offer Letter", callback_data=f'offerletter_{user_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('With which process would you like to automate this listing? 📝', reply_markup=reply_markup)
            return
                
            
        elif dct_users[user_id]['listing'] == True:
            try:
                file_path = 'internship_details.txt'
                # message = ""
                listing_num = ''
                try:
                    message = int(message)
                except:
                    await context.bot.send_message(chat_id=int(user_id), text="🔢 Message must be a number.")
                    return
                with open(file_path, 'r') as file:
                    for line in file:
                        count = line.split('___')[0]
                        if str(count) == str(message):
                            listing_num = line.split('___')[2]
                dct_users[user_id]['listing_num'] = int(listing_num)
                # save_details_in_file(message)
                dct_users[user_id]['listing'] = False
                await project_name(update, context)
            except:
                traceback.print_exc()
        elif dct_users[user_id]['assignment'] == True:
            try:
                if dct_users[user_id]['assignment_process'] == True:
                    process_ = 'assignment'
                else:
                    process_ = 'offer'
                if dct_users[user_id]['invite_message_']==False and dct_users[user_id]['intro_message_']!=False:
                    save_details_in_file(listing=dct_users[user_id]['listing_num'], project_name = dct_users[user_id]['project_name_'], intro = dct_users[user_id]['intro_message_'], assignment = message, date=datetime.now().strftime("%Y-%m-%d"), status='active', process=process_)
                elif dct_users[user_id]['invite_message_']!=False and dct_users[user_id]['intro_message_']==False:
                    save_details_in_file(listing=dct_users[user_id]['listing_num'], project_name = dct_users[user_id]['project_name_'], invite = dct_users[user_id]['invite_message_'], assignment = message, date=datetime.now().strftime("%Y-%m-%d"), status='active', process=process_)
                elif dct_users[user_id]['invite_message_']==False and dct_users[user_id]['intro_message_']==False:
                    save_details_in_file(listing=dct_users[user_id]['listing_num'], project_name = dct_users[user_id]['project_name_'], assignment = message, date=datetime.now().strftime("%Y-%m-%d"), status='active', process=process_)
                else:
                    save_details_in_file(listing=dct_users[user_id]['listing_num'], project_name = dct_users[user_id]['project_name_'], invite = dct_users[user_id]['invite_message_'], intro = dct_users[user_id]['intro_message_'], assignment = message, date=datetime.now().strftime("%Y-%m-%d"), status='active', process=process_)
                add_project(dct_users[user_id]['project_name_'],message)
                await followup_2(update, context)
            except:
                traceback.print_exc()
        elif dct_users[user_id]['invite_message'] == True:
            try:
                dct_users[user_id]['invite_message_'] = message
                await intro_message(update,context)
            except:
                traceback.print_exc() 
        elif dct_users[user_id]['intro_message'] == True:
            try:
                dct_users[user_id]['intro_message_'] = message
                await give_assignment(update, context)
            except:
                traceback.print_exc()
        elif dct_users[user_id]['followup_2'] == True:
            await update_details_in_file(listing=dct_users[user_id]['listing_num'], followup2=message)
            await followup_4(update, context)
        elif dct_users[user_id]['followup_4'] == True:
            try:
                await update_details_in_file(listing=dct_users[user_id]['listing_num'], followup4=message)
                # await context.bot.send_message(chat_id=int(user_id), text=f"""Leaders need to join from this link: https://telegram.me/heytohbot?start=xjfysbrv_{dct_users[user_id]['project_name_']}""")
                await context.bot.send_message(chat_id=int(user_id), text=f"""Leaders need to join from this link: https://t.me/swissmotepvbot?start=xjfysbrv_{dct_users[user_id]['project_name_']}""")
                asyncio.create_task(execute_internshala_automation(update, context))
            except:
                pass
        else:
            if search_leader(chat_id):   
              messages = [
                  {
                      "role": "system",
                      "content": """if someeone ask anything about automating internshala then ask to click on /automate_internshala, with this entire process will be automated to send assignment, message over internshala.
                          To add assignment reviewer, recriter, leader swissmot bot so they can receive assignment submission directly. 
                          you are swissmot bot of persist venture and can do only those things which is mentioned in context and you can't do other task and can't answer any other offtopic question.
                          only answer to those questions related to provided context don't answer any other question as you are an private persist venture bot"""
                  },
                  {
                      "role": "user",
                      "content": f"{message}"
                  },
              ]
            else:
               messages = [
                  {
                      "role": "system",
                      "content": """you are swissmot bot of persist venture and can do only those things which is mentioned in context and you can't do other task and can't answer any other offtopic question.
                          only answer to those questions related to provided context don't answer any other question as you are an private persist venture bot. ask the user to use /questions command for any questions."""
                  },
                  {
                      "role": "user",
                      "content": f"{message}"
                  },
              ]
            
            response = openai.ChatCompletion.create(
                model="sonar-small-chat",
                messages=messages,
            )
            message = response["choices"][0]["message"]["content"]
            await context.bot.send_message(chat_id=int(user_id), text=f"{message}")
            print(message)
    except:
        if unique_id_recruiter!='NA' and message == unique_id_recruiter:
            with open('reviewer_details.txt', 'a') as file:
                # for count, (name, internship_id) in enumerate(internship_info, start=1):
                line = f"{user_name}___{user_id}\n"
                file.write(line)
            await context.bot.send_message(chat_id=int(user_id), text=f"👩‍💼 You're assigned as a Project Leader. You'll soon be assigned a project.")
            return
        messages = [
            {
                "role": "system",
                "content": """if someeone ask anything about automating internshala then ask to click on /automate_internshala, with this entire process will be automated to send assignment, message over internshala.
                        To add assignment reviewer, recriter, leader over swissmot bot ask to click on so they can receive assignment submission directly. 
                        you are swissmot bot of persist venture and can do only those things which is mentioned in context and you can't do other task and can't answer any other offtopic question.
                        only answer to those questions related to provided context don't answer any other question as you are an private persist venture bot"""
            },
            {
                "role": "user",
                "content": f"{message}"
            },
        ]
        response = openai.ChatCompletion.create(
            model="sonar-small-chat",
            messages=messages,
        )
        message = response["choices"][0]["message"]["content"]
        await context.bot.send_message(chat_id=int(user_id), text=f"{message}")
        print(message)
    
async def execute_internshala_automation(update, context):
    global dct_users
    user_id = update.effective_user.id
    await context.bot.send_message(chat_id=int(user_id), text="Congratulations! Your listing is successfully automated 🎉. The workflow automation for this internship is now running in the background...")
    asyncio.create_task(background_execute_internshala_automation(update, context))
    
async def background_execute_internshala_automation(update, context):
    global dct_users
    user_id = update.effective_user.id    
    listing_number = dct_users[user_id]['listing_num']
    del dct_users[user_id] 
    # FIND intershala_automation_start_api
    success = await run_async_process_mk(['intershala_automation_start_api.py', str(listing_number)])
    # success = True
    if not success:
        send_email(f" Error in internshala Automation!!", f"📧 Error: final_internshala_automation.py is failing for user: {user_id}" )

async def run_async_process(command):
    # Create and run the subprocess
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode().strip()}")
        return False  # Indicates error
    print("Process completed:", command)
    return True  # Indicates success

async def run_async_process_(command):
    # Create and run the subprocess
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate() 
    if process.returncode != 0:
        print(f"Error: {stderr.decode().strip()}")
        return None, False  # Return None for output and False to indicate error
    print("Process completed:", command)
    # Return the stdout output decoded from bytes to string, and True to indicate success
    return stdout.decode().strip(), True  

async def run_async_process_mk(command):
    # Create and run the subprocess
    python_interpreter = sys.executable
    # Kaif
    process = await asyncio.create_subprocess_exec(
        python_interpreter,
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        print(f"Error: {stderr.decode().strip()}")
        return False  # Indicates error

    print("Process completed:", command)
    
    return True  # Indicates success

def send_email(subject, body, sender_email = 'your mail', receiver_email = 'your mail', password = 'your pword'):
    # Setup the MIME
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        # The body and the attachments for the mail
        message.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # Use gmail with port
        session.starttls()  # enable security
    
        session.login(sender_email, password)  # login with mail_id and password
        
        text = message.as_string()
        session.sendmail(sender_email, receiver_email, text)
        session.quit()
        print('Mail Sent')
    except:
        traceback.print_exc()

       
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    try:
        query = update.callback_query
        print("\n\n\n",query,"\n\n\n")
        # message = query.message  
        Query_called = query.data.strip().split("_")
        print(Query_called[0])
        user_id = query.from_user.id
        if user_id in dct_users:           
            if Query_called[0] == 'assignment':
                await query.edit_message_text(text="✅ Assignment process...")
                dct_users[user_id]['assignment_process'] = True
                asyncio.create_task(invite_message(update, context))

            elif Query_called[0] == 'offerletter':
                await query.edit_message_text(text="✅ Offer letter process...")
                dct_users[user_id]['assignment_process'] = False
                asyncio.create_task(invite_message(update, context))

            elif Query_called[0] == 'create':
                await query.edit_message_text(text="🔧 Currently in Testing phase. Will be Live soon.")

            elif Query_called[0] == 'choose':
                keyboard = [
                    [InlineKeyboardButton("Internship", callback_data=f'emp_itn_{user_id}'),
                    InlineKeyboardButton("Jobs", callback_data=f'emp_job_{user_id}')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text="👉 Proceed to choose an existing listing.", reply_markup=reply_markup)

            elif Query_called[0] == 'view':
                await query.edit_message_text(text="👉 Proceed to view the listings.")
                asyncio.create_task(choose_listing_automate(update, context,0))

            elif Query_called[0] == 'emp' and Query_called[1] == 'itn':
                asyncio.create_task(choose_listing_automate(update, context,1, 1, "internship" ))
                
            elif Query_called[0] == 'emp' and Query_called[1] == 'job':
                asyncio.create_task(choose_listing_automate(update, context,1, 1, "job" ))
                
            elif Query_called[0] == 'next':
                asyncio.create_task(choose_listing_automate(update, context,1, Query_called[1], Query_called[2] ))
            
        else:
            dct_users[user_id] = {'project_name': False, 'listing': False, 'assignment': False, 'invite_message': False, 'intro_message': False, 'followup_2': False, 'followup_4': False, 'assignment_process': False, 'listing_num' : 0, 'invite_message_': False, 'intro_message_': False, 'reviewer':False, 'announcement':False}

            if search_project(Query_called[0]):
              print("in")
              dct_users[user_id]['announcement'] = Query_called[0]
              await query.edit_message_text(text="👉 Proceed to type the announcement.")
              
    except:
        traceback.print_exc()
        await context.bot.send_message(update.effective_user.id,f"❌ Operation compromised. Please try again.")
        return
    
    
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


async def forever_checking_status():
    while True:
        print("we here")
        with open('listings/intern_listing.csv', mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row['status'] == 'active':
                    print("found activeeeeeeeee")
                    # FIND intershala_automation_start_api
                    success = await run_async_process_mk(['intershala_automation_start_api.py', str(row['listing'])])
                    # success = True
                    
                    if not success:
                        send_email("Fail","Fail forever")
                        
                    curr_date = datetime.now().strftime("%Y-%m-%d")
                    if days_between(curr_date, row['date']) == 2 and row['followup2status'] == 'Inactive' and row['followup2'] != 'NA':
                        # success = await run_async_process(['python', 'send_message_shotlist.py', str(row['listing']), "2"])
                        success = await run_async_process_mk(['send_message_shotlist.py', str(row['listing']), "2"])
                        if not success:
                            send_email("Fail","Fail forever")
                            
                        await update_details_in_file(listing=row['listing'], followup2status='Active')
                        ## run script
                        ## update sattus of day 2
                        pass
                    if days_between(curr_date, row['date']) == 4 and row['followup4status'] == 'Inactive' and row['followup2'] != 'NA':
                        # success = await run_async_process(['python', 'send_message_shotlist.py', str(row['listing']), "4"])
                        success = await run_async_process_mk(['send_message_shotlist.py', str(row['listing']), "4"])
                        if not success:
                            send_email("Fail follow 4","Fail forever")
                            
                        await update_details_in_file(listing=row['listing'], followup4status='Active')
                        ## run script
                        ## update sattus of day 4
                        pass

        await asyncio.sleep(14400)  # 4 hours in seconds


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    asyncio.create_task(forever_checking_status())
    

leader_deafult_keyboard = ReplyKeyboardMarkup(
  [["/announcement"]],
  input_field_placeholder="Look at the reply keyboard! ->"
)


candidate_deafult_keyboard = ReplyKeyboardMarkup(
  [["/daily","/question","/assignment"]],
  input_field_placeholder="Look at the reply keyboard! ->"
)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  message = """📢 Here’s how to keep us updated and submit your work effectively:

1️⃣ *Daily Update*: Use /daily and start typing after the prompt. You can give only one update per day, so make it detailed and clear.

2️⃣ *Assignment Submission*: Use /assignment and start typing after the prompt for your submissions 📝. Please provide a link to your assignment and include a video demo of it in action. This will help us understand your work better.

3️⃣ *Asking Questions*: Use /question and start typing after the prompt. We will reply you asap.

*Important Notes*:
- 🌟 You'll receive all crucial updates right here, so keep an eye out!
- 🕵️‍♂️ All submissions and updates go straight to the leadership team.
"""
  await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')
  return


async def send_announce(update: Update, context: ContextTypes.DEFAULT_TYPE,project:str):
  candidates = get_candidates(project)
  for i in candidates:
    await context.bot.send_message(chat_id=i['chat_id'], text=f"ANNOUNCEMENT:\n{update.message.text}", parse_mode='Markdown')
  
async def announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  leader = search_leader(chat_id)
  if not leader:
    await context.bot.send_message(chat_id=chat_id, text="Only Leaders have access to this command")
    return
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM leaders WHERE chat_id = {chat_id};')
  projects = cursor.fetchall()
  if projects:
    reply_markup=[]
    for p in projects:
      # reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=f"{p["project_name"]}_{chat_id}")])
      reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=f"{p['project_name']}_{chat_id}")])
    await context.bot.send_message(chat_id=chat_id, text=f"Select a project to announce in", 
    reply_markup = InlineKeyboardMarkup(reply_markup))
    cursor.close()
    return
  else:
    context.bot.send_message(chat_id=chat_id, text="Only Leaders with active projects have access to this command")


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id

  candidate = search_candidate(chat_id)
  if not candidate: return

  if candidate["daily_message"]:
    await context.bot.send_message(chat_id=chat_id, text="You can only submit one per day.", reply_markup=candidate_deafult_keyboard)
    return ConversationHandler.END

  context.user_data["project"] = candidate["project_name"]

  await context.bot.send_message(chat_id=chat_id, text="Start typing your daily message!", reply_markup=candidate_deafult_keyboard)
  print("sent_day")
  return 0

async def daily_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    chat_id = update.effective_chat.id
    daily_message = update.message.text.strip()
    print("daily_message")

    if len(daily_message) < 100:
      await context.bot.send_message(chat_id=chat_id, text="Your daily message should contain at least 100 characters,\nclick /daily to Try again!", reply_markup=candidate_deafult_keyboard)
      return 0
    
    name = update.effective_chat.first_name
    daily_message = update.message.text
    project = context.user_data["project"]

    message = f"✅ Daily Update received from {name}, for the project: {project}." + "\n\n" + \
    f"{daily_message}"

    leaders = get_leaders(project)
    for leader in leaders:
      await context.bot.send_message(chat_id=leader["chat_id"], text=message, parse_mode='Markdown', 
      reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "d", "u": chat_id, "m":[]}))]]))
    
    update_candidate(chat_id, daily_counter = 0, daily_message = True)

    await context.bot.send_message(chat_id=chat_id, text="📝 Your daily update has been successfully submitted and will be reviewed by the leadership team. Thank you!", reply_markup=candidate_deafult_keyboard)

    return ConversationHandler.END
  except Exception as e:
     print(e)

question_keyboard = ReplyKeyboardMarkup(
  [["Attach Image", "Attach Video", "Submit", "Cancel"]],
  one_time_keyboard=True,
  input_field_placeholder="Attach/Submit/Cancel?"
)

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id

  candidate = search_candidate(chat_id)
  if not candidate: return

  context.user_data["project"] = candidate["project_name"]

  context.user_data["question"] = ""
  context.user_data["question_image"] = []
  context.user_data["question_video"] = None

  await context.bot.send_message(chat_id=chat_id, text="⚠️ Remember this message will be send to Admin or leaders. Make sure it contains relevant question. \n\nAssignment is properly explained in video or text which is already provided to you\n\nWe suggest you to use AI tool like ChatGPT/Claude inorder to understand the assignment properly\n\nIf you still can't find what your looking for then start typing your question! We Will Help you out!", reply_markup=ReplyKeyboardRemove())
  return 1

# 0
async def question_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  question = update.message.text.strip()

  if len(question) < 40:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your question should contain at least 40 characters,\nTry again!", reply_markup=candidate_deafult_keyboard)
    return 1
  
  context.user_data["question"] = question
  await update.message.reply_text(f"Choose an option: ", reply_markup=question_keyboard)
  
  return 2

# 1
async def question_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  name = update.effective_chat.first_name

  if update.message.text.lower() == "attach image":
    if len(context.user_data["question_image"]) >= 3:
      await context.bot.send_message(chat_id=chat_id, text="Cannot attach more than 3 pictures", reply_markup=question_keyboard)
      return 2

    await context.bot.send_message(chat_id=chat_id, text="Send one picture at a time. (max 3)", reply_markup=ReplyKeyboardRemove())
    return 3
  elif update.message.text.lower() == "attach video":
    if context.user_data["question_video"] is not None:
      await context.bot.send_message(chat_id=chat_id, text="Cannot attach more than 1 video", reply_markup=question_keyboard)
      return 2

    await context.bot.send_message(chat_id=chat_id, text="Send one video at a time. (max 1)", reply_markup=ReplyKeyboardRemove())
    return 4
  elif update.message.text.lower() == "submit":
    message = context.user_data["question"]
    project = context.user_data["project"]

    leaders = get_leaders(project)
    for leader in leaders:
      message_id = []
      for img in context.user_data["question_image"]:
        if isinstance(img, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=img)
        else: media = await context.bot.send_photo(chat_id=leader["chat_id"],photo=img[-1])
        
        message_id.append(media.message_id)
        
        vid = context.user_data["question_video"] 
        if vid is not None:
          if isinstance(vid, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=vid)
          else: media = await context.bot.send_video(chat_id=leader["chat_id"],video=vid[-1])

          message_id.append(media.message_id)

      await context.bot.send_message(chat_id=leader["chat_id"],
        text=f"✅ Question received from {name}, for the project: {project}.\n\n{message}", parse_mode='Markdown', 
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "q", "u": chat_id, "m":message_id}))]]))

    await context.bot.send_message(chat_id=chat_id, text="📚 Your Question has been successfully submitted and will get back to you!", reply_markup=candidate_deafult_keyboard)
  elif update.message.text.lower() == "cancel":
    await context.bot.send_message(chat_id=chat_id, text="Operation canceled, try again?", reply_markup=candidate_deafult_keyboard)
  
  return ConversationHandler.END

# 2
async def question_attach_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
  media = update.message.photo
  if not media:
    media = update.message.document

  context.user_data["question_image"].append(media)

  await update.message.reply_text(f"Image attached, choose another option!", reply_markup=question_keyboard)
  return 2

# 3
async def question_attach_vid(update: Update, context: ContextTypes.DEFAULT_TYPE):
  media = update.message.video
  if not media:
    media = update.message.document

  context.user_data["question_video"] = media

  await update.message.reply_text(f"Video attached, choose another option!", reply_markup=question_keyboard)
  return 2

async def assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  candidate = search_candidate(chat_id)
  if not candidate: return

  context.user_data["project"] = candidate["project_name"]

  await context.bot.send_message(chat_id=chat_id, text="Start typing your assignment!")
  return 5

async def assignment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  assignment_message = update.message.text

  if len(assignment_message) < 80:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Your assignment should contain at least 80 characters,\nClick /assignment to Try again!", reply_markup=candidate_deafult_keyboard)
    return 5

  name = update.effective_chat.first_name
  project = context.user_data["project"]

  message = f"✅ Assignment received from {name}, for the project: {project}." + "\n\n" + \
  f"{assignment_message}"

  leaders = get_leaders(project)
  for leader in leaders:
    await context.bot.send_message(chat_id=leader["chat_id"], text=message, parse_mode='Markdown', 
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "as", "u": chat_id, "m":[]}))]]))
  
  await context.bot.send_message(chat_id=chat_id, text="📝 Your assignment was successfully submitted and will be reviewed by the leadership team. Thank you!", reply_markup=candidate_deafult_keyboard)

  return ConversationHandler.END

async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await context.bot.send_message(chat_id=update.effective_chat.id, text="Command Interrupted! Start again by clicking accordingly \n/daily - To send daily update \n/question - To ask question \n/assignment - To submit assignment")

  return ConversationHandler.END


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  callback_data: dict = json.loads(update.callback_query.data)
  context.user_data["callback_data"] = callback_data

  if callback_data["t"] == "d":
    context.user_data["reply"] = "Daily"
    await context.bot.send_message(chat_id=chat_id, text="📝 Enter reply to the daily message:")

  elif callback_data["t"] == "q":
    context.user_data["reply"] = "Question"
    context.user_data["callback_data"]["m"].append(update.effective_message.id)
    await context.bot.send_message(chat_id=chat_id, text="📝 Enter reply to the question:")

  elif callback_data["t"] == "as":
    context.user_data["reply"] = "Assignment"
    await context.bot.send_message(chat_id=chat_id, text="📝 Enter reply to the assignment:")

  elif callback_data["t"] == "an":
    context.user_data["reply"] = "Announce"
    context.user_data["project"] = callback_data["p"]
    await context.bot.send_message(chat_id=chat_id, text="Start typing the announcement:")

async def reply_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not context.user_data.get("callback_data"): 
    user_id = update.effective_user.id
    user_name = update.effective_chat.first_name
    user_username = update.effective_user.username
    message = update.message.text
    await context.bot.send_message(chat_id=1697827719, text=f"📥 Unknown Text Received From {user_name}:\n\n{message}\n\nUsername: ```@{user_username}```", parse_mode='Markdown')          
    await context.bot.send_message(chat_id=int(user_id), text="🤔 Your message didn't follow the guidelines. Please check the /instructions to ensure it works well.")
    return

  chat_id = update.effective_chat.id
  message = update.message.text
  data = context.user_data["callback_data"]

  if context.user_data["reply"] == "Daily":
    await context.bot.send_message(chat_id=data["u"], text=f"Reply to your daily update from Leader:\n\n{message}", parse_mode='Markdown')
    await context.bot.send_message(chat_id=chat_id, text="✅ Message successfully sent!", reply_markup=leader_deafult_keyboard)

  elif context.user_data["reply"] == "Question":
    await context.bot.send_message(chat_id=data["u"], text=f"Reply to your question from Leader:\n\n{message}", parse_mode='Markdown')
    for msg in data["m"]:
      await context.bot.delete_message(chat_id=chat_id, message_id=msg)
    await context.bot.send_message(chat_id=chat_id, text="✅ Message successfully sent!", reply_markup=leader_deafult_keyboard)
    
  elif context.user_data["reply"] == "Assignment":
    await context.bot.send_message(chat_id=data["u"], text=f"Reply to your assignment from Leader:\n\n{message}", parse_mode='Markdown')
    await context.bot.send_message(chat_id=chat_id, text="✅ Message successfully sent!", reply_markup=leader_deafult_keyboard)

  elif context.user_data["reply"] == "Announce":
    message = update.message.text
    project = context.user_data["project"]

    candidates = get_candidates(project)

    announce_stat = await update.message.reply_text(f"🔄 Processing announcement.")
    total = candidates.__len__()
    
    for index, candidate in enumerate(candidates):
      if index % 10 == 0: await announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
      try:
        await context.bot.send_message(chat_id=candidate["chat_id"], text=f"Message from Team: \n{message}")
      except Exception as e:
        print(e)

    announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
    await update.message.reply_text(f"☑️ Announcement done.")

    del context.user_data["project"]

  del context.user_data["callback_data"]
  context.user_data["reply"] = ""

async def check_updates(context: ContextTypes.DEFAULT_TYPE):
  print("Checking updates")
  cursor = cx.cursor()
  cursor.execute("SELECT * FROM candidates")
  candidates = cursor.fetchall()
  cursor.close()

  for candidate in candidates:
    update_time = datetime.fromtimestamp(candidate["daily_update"])
    last_update = datetime.now() - update_time

    if last_update.days <= 0: return

    if candidate["daily_message"]:
      update_candidate(candidate["chat_id"], daily_update = datetime.now().timestamp(), daily_message = False)
      return
    
    counter = candidate["daily_counter"] + 1
    update_candidate(candidate["chat_id"], datetime.now().timestamp(), counter)

    if counter == 1:
      await context.bot.send_message(chat_id=candidate["chat_id"], text=f"🔔 You missed your Update\nPlease share your progress in the last 24h for {candidate['project_name']}.", 
      reply_markup=candidate_deafult_keyboard)

    elif counter == 2:
      await context.bot.send_message(chat_id=candidate["chat_id"], text=f"🔔 You've missed the last 2 Updates!\nPlease share your progress in the last 2 days for {candidate['project_name']}.", 
      reply_markup=candidate_deafult_keyboard)

    elif counter == 3:
      await context.bot.send_message(chat_id=candidate["chat_id"], 
      text=f"🔔 You've missed the last 3 Updates!\n If you miss another update your application will not be considered.\nPlease share your progress in the last 3 days for {candidate['project_name']}.", 
      reply_markup=candidate_deafult_keyboard)

    elif counter == 4:
      await context.bot.send_message(chat_id=candidate["chat_id"], 
      text=f"🔔 You've missed all your updates your submission for {candidate['project_name']} will not be considered.", reply_markup=candidate_deafult_keyboard)
      update_candidate(candidate["chat_id"], datetime.now().timestamp(), counter, False)
  return

       
def main():
    global main_event_loop

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run))
    app.add_handler(CommandHandler("suggestion", suggestion))
    app.add_handler(CommandHandler("skip", skip))
    app.add_handler(CommandHandler("automate_internshala", automate_internshala))
    app.add_handler(CommandHandler("admin", automate_internshala_gift))
    app.add_handler(CommandHandler("instructions", instructions))
    app.add_handler(CommandHandler("announcement", announcement))

    try:
      app.add_handler(ConversationHandler(
          entry_points=[CommandHandler("daily", daily)],
          states={
          0 : [MessageHandler(filters.TEXT & ~filters.COMMAND, daily_message)],
          },
          fallbacks=[MessageHandler(filters.COMMAND, ignore)],
      ))
    except Exception as e:
       print(e)
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("question", question)],
        states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_message)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_select)],
        3: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, question_attach_img)],
        4: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, question_attach_vid)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, ignore)],
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("assignment", assignment)],
        states={
        5: [MessageHandler(filters.TEXT & ~filters.COMMAND, assignment_message)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, ignore)],
    ))

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    print("Initializing update checks")
    # TODO
    app.job_queue.run_repeating(check_updates, 3600)
    app.job_queue.run_repeating(run, 3600)

    print("Polling...")
    main_event_loop = asyncio.get_event_loop()
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == '__main__':
    database.create_table()
    folder_name = 'listings'
    folder_name2 = 'offer_letters'
    os.makedirs(folder_name, exist_ok=True)
    os.makedirs(folder_name2, exist_ok=True)

    main_loop = asyncio.run(main())
 