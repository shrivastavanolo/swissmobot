import aiofiles
import helper # LLM function
from time import sleep
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, ReplyKeyboardRemove
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
from queries import query_get_many, update_project, query_update, query_get_one
import form
import sys
from intershala_automation_start_api import get_all_shortlisted_applicants, send_message_using_id
from pathlib import Path
######### To do: Set your email at function 'send_email' ############

# APIs and tokens
unique_id_recruiter = 'NA'
openai.api_key = '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'
# openai.api_base = 'https://api.perplexity.ai'
openai.api_base = 'https://api.openai.com'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# KAIF
TOKEN = '6119880672:AAGPBH_bjHYeeCs31tpk0vMNCVjvklzDtiI'
# swissmote pv
# TOKEN = '7098210763:AAGcqaIofG1mE_KtZkEVGroOVJPK4Tnzoew'

dct_users = {}

#### /start for new session
#### /start xjfysbrv_<project> for new leaders
#### /start dewdrop_<project> for assignment candidates
#### /start rcbwin_<project> for offerletter candidates

#start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args: list = context.args
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    name = update.effective_chat.first_name
    
    print('args: ', args)
    if not args:
      is_leader = search_leader(chat_id=chat_id)
      if is_leader:
        message = "Welcome to Swissmote Bot, exclusively for Persist Venture! 🎉" \
      "I'm here to streamline your workflow with specialized functions:" \
      "✨ For a simplified recruiting process (Assignment or Offer Letter), including automated sending assignments, messages, invites, shortlisting, and hiring on Internshala, use the command: /automate_internshala. This will ensure a fully automated process, eliminating the need for manual intervention." \
      "🌟 Connect with our Vision:(https://www.youtube.com/watch?v=itGNk0wellQ) 🎥"
      else:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot," + "\n" + \
      "you are already a candidate for another project. Use /instructions to know more."
      
      await update.message.reply_text(text=message)
      return
    
    global dct_users
    project: str = args[0]  
    project_split = project.split('_')[1]
    
    if project.startswith("xjfysbrv_"):
      #new Leader enters here using /start xjfysbrv_<project>
      project = project.split("_")[1]
      print('project: ')
      if search_project(project_split) is None:
        await update.message.reply_text("Invalid argument!")
        return
      
      leader = add_leader(user_id, project_split)
      if leader:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot2.0." + "\n" + \
      "Here, you'll receive all assignment submissions and daily updates. 📬" + "\n" + \
      "Plus, you can mass messages directly to everyone—just send it to me, and I will personally send this message to everyone 📢" + "\n" + \
      "Let’s dive in! 💪"
      else:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot2.0," + "\n" + \
      "you are already a leader for this project."
      await update.message.reply_text(message, reply_markup=leader_deafult_keyboard)
    else:
      # print(project)
      project_details = search_project(project_split)
      # print(project_details)
      # #if project doesnt exist
      if project_details is None:
        await update.message.reply_text("Invalid argument!")
        return 
      # TODO uncomment
      candidate = add_candidate(user_id, project.split("_")[1], int(datetime.now().timestamp()))
        #if candidate already belongs to another project (can't have 2 projects at the same time)
      if not candidate:
        message = f"🎉 Hello {name}! Welcome to SwissmoteBot," + "\n" + \
        "you are already a candidate for another project. Use /instructions to know more."
        await update.message.reply_text(message)
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
        # await update.message.reply_text(project_details["assignment"], reply_markup=candidate_deafult_keyboard)
        # return

      elif project.startswith("rcbwin_"):
        #offer letter candidate
        
        try:
          project_split = project.split('_')[1]
          context.user_data['project'] = project_split
          # await update.message.reply_text(project_details["assignment"], reply_markup=candidate_deafult_keyboard)
          # await update.message.reply_text(text="Please enter your full name to proceed with the offer letter process. 📄✨")
          await candidate_signup(update, context)
                        
          # await context.bot.send_message(chat_id=chat_id, text="⏳ Please wait while we process your offer letter... 📝")
          # try:
          #   form.pdf_top(name=full_name,
          #               filepath=f"offer_letters/{full_name}_{project_split}_offerletter.pdf"
          #             )
          # except:
          #   print('really bro')
          # return 6
          # await context.bot.send_document(chat_id=chat_id, document=open(f"offer_letters/{full_name}_{project_split}_offerletter.pdf","rb"))
        except Exception as e:
          print(e)

      print('give count')
      #sends a candidate count to the project leader whenever new candidate joins  
      candidate_count = query_get_one("SELECT COUNT(*) as count FROM candidates WHERE project_name = ?", [project.split('_')[1]])
      print(candidate_count['count'])
      message = "🌟 New Applicant! 🌟" + "\n" + \
      f"{name} has just joined SwissmoteBot for the {project.split('_')[1]} Assignment" + "\n" + \
      "We gave them an warm welcome and succesfully Sent Assignment!" + "\n" + \
      f"Total Applicants: {candidate_count['count']}"
      leaders = get_leaders(project.split('_')[1])
      for leader in leaders:
        print(leader)
        if not leader["join_message"]:
          print('not leader["join_message"]')
          join_message = await context.bot.send_message(chat_id=leader["chat_id"], text=message)
        else:
          print('else from join message')
          await context.bot.delete_message(chat_id=leader["chat_id"], message_id=leader["join_message"])
          join_message = await context.bot.send_message(chat_id=leader["chat_id"], text=message)
        update_leader(leader["chat_id"], join_message.message_id)      
    return

async def initiate_offerletter(update: Update, context:ContextTypes.DEFAULT_TYPE):
  print('initiate offerletter')
  await update.message.reply_text(text="Please enter your full name to proceed with the offer letter process. 📄✨")
  return 6
  
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
    
    if emp_type == 'internship':   
        file_path = "internship_details.txt"
        
    elif emp_type == 'job' :
        file_path = 'job_details.txt'
        
    message = ""
    active_projects = query_get_many('''
                                     SELECT listing
                                     FROM projects
                                     WHERE status = 1
                                    ''')
    active_listing = []
    for project in active_projects:
      for listing_num in project:
        active_listing.append(listing_num)

    # print(active_listing)
    with open(file_path, 'r') as file:
      for line in file:
        split_line = line.split('___')
        count = split_line[0]
        name = split_line[1]
        package = split_line[3]
        # print(split_line[2], active_listing, split_line[2] in active_listing)      
        # sleep(1)  
        if 'None' in package:
          message = message + f"{count}. {name}\n\n"
        else:
          if int(split_line[2]) in active_listing:
            print('ACTIVE ' , '🟢'*7)
            message = message + f"{count}. {name} 🟢 \n{package}\n"
            active_listing.remove(int(split_line[2]))
          else:
            message = message + f"{count}. {name}  \n{package}\n"
                    
    if message == "":
      await update.callback_query.edit_message_text(text="That's All ✅", parse_mode='Markdown')
    else:
      if flag == 1:
        add = '🟢 represent an Active project on a Listing \n\n'
        add += message
        add += "🔢 Enter the Listing Number, Please!"
        await context.bot.send_message(chat_id=int(user_id), text=add, parse_mode='Markdown', reply_markup=reply_markup)
        await listing(update, context)
        return
        
        
    
#Automate internshala command starts here
async def automate_internshala(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  user_id = update.effective_user.id
  if not search_leader(chat_id=user_id):
    await update.message.reply_text('🚨 Only leaders can use this command 🚨')
    return
  asyncio.create_task(background_automate_internshala(update, context))
  
async def automate_internshala_gift(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  asyncio.create_task(background_automate_internshala(update, context))
    
#bg automation
async def background_automate_internshala(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    user_id = update.effective_user.id
        
    # await update.message.reply_text('Welcome to Fully Automated Funnel 🚀')
    # FIND initial dct_users
    dct_users[user_id] = {'project_name': False, 'listing': False, 'assignment': False, 'invite_message': False, 'intro_message': False, 'followup_2': False, 'followup_4': False, 'assignment_process': False, 'listing_num' : 0, 'invite_message_': False, 'intro_message_': False, 'reviewer':False}
    keyboard = [
      [
        InlineKeyboardButton("📝 Create New Listing", callback_data=f'create_{user_id}'),
        InlineKeyboardButton("🔍 Choose Listing", callback_data=f'choose_{user_id}'),
      ],
      [
        InlineKeyboardButton("✉ Set Invite message ", callback_data=f'setinvite_{user_id}'),
        InlineKeyboardButton("✉ Set Assignment message", callback_data=f'setassignment_{user_id}'),
      ],
      [
        InlineKeyboardButton("📩 Get Current Invite and Assignment message ", callback_data=f'getmessages_{user_id}'),
      ],
      [
        InlineKeyboardButton("🏃‍♂️ Active Listings ", callback_data=f'active_{user_id}'),
        InlineKeyboardButton("❌ Closed Listings", callback_data=f'close_{user_id}'),
      ],
      [
        InlineKeyboardButton("📢 Announcement", callback_data=f'makeannouncement_{user_id}')
      ]
    ]

    #admin keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("""**Admin Dashboard 📃📊**

Hire the best talents from around the world 🌍. Send assignments ✍️ and review them right here 📝. Create offer letters for hired candidates 📄. You can even ban users for misbehaving 🚫. Simplify your hiring process with SwissmoBot!

""", reply_markup=reply_markup, parse_mode='Markdown')

async def candidate_signup(update: Update, context:ContextTypes.DEFAULT_TYPE):
  print('candidate_signup')
  user_id = update.effective_chat.id
  global dct_users
  # deleted in handle_name
  dct_users[user_id] = {'candidate_login':True}

  # try:
  #   if user_id not in dct_users:
  #   # Initialize it with an empty dictionary if not present
  #     dct_users[user_id] = {}

  #   dct_users[user_id]['candidate_login'] = True
  # except:
  #   print('big break')
  await context.bot.send_message(chat_id=user_id, text="Please enter your full name to proceed with the offer letter process. 📄✨")
    
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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    
    await context.bot.send_message(chat_id=int(user_id), text="Enter Project Name:")

async def listing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  # print('inside listing...')
    
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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False   

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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    
    if dct_users[user_id]['assignment_process'] == True:
        message= f"""
📝 Submit link to the assignment either in form of notion doc or loom video 🖇️
"""
# Suggestions? Use /suggestion."""
# A Swissmote link : https://t.me/swissmotepvbot?start=dewdrop_{dct_users[user_id]['project_name_']}
        await context.bot.send_message(chat_id=int(user_id), text=message)
    else:
        message= f"""
📝 Hired Message
Please enter the hired message as per the offer letter process.

"""
# Suggestions? Use /suggestion."""
# Keep Swissmote.0 link : https://t.me/swissmotepvbot?start=rcbwin_{dct_users[user_id]['project_name_']}
        await context.bot.send_message(chat_id=int(user_id), text=message)
    # 5233340898

# using to set invite (writing to text file)
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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    # if dct_users[user_id]['assignment_process'] == True:
    await context.bot.send_message(chat_id=int(user_id), text="""
📝 *Invitation Message*
Enter an invite message to be sent to the Internshala provided database.
""", parse_mode='Markdown')
    
# using to set Assignment (writing to text file)
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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    
    if dct_users[user_id]['assignment_process'] == True:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 Assignment Message
📥 Enter the assignment message for candidates who have applied for this job.

🔗✨ Make sure to add this inside the assignment text: `xx_link_xx`
""")
    else:
        await context.bot.send_message(chat_id=int(user_id), text="""
📝 Assignment Message
📥 Enter the assignment message for candidates who have applied for this job.

🔗✨ Make sure to add this inside the assignment text: `xx_link_xx` 
""")
#         await context.bot.send_message(chat_id=int(user_id), text="""
# 📝 *Introduction Message*
# Enter an intro message for candidates who have applied for this job.

# To skip, use */skip*. For suggestions, use */suggestion*.""", parse_mode='Markdown')
#     else:
#         await context.bot.send_message(chat_id=int(user_id), text="""
# 📝 *Introduction Message*
# Enter an intro message for candidates who have applied for this job.

# To *skip*, use */skip*. For *suggestions*, use */suggestion*.""", parse_mode='Markdown')


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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    
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
    
    dct_users[user_id]['dailyupdate'] = False
    dct_users[user_id]['assignmentsubmission'] = False
    dct_users[user_id]['question'] = False
    dct_users[user_id]['candidate_login'] = False
    
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
                  await context.bot.send_message(chat_id=int(user_id), text=f"""
📝 *Assignment Submission*
Please provide your assignment. Make sure it includes:

- link to the assignment 🖇️
- Loom video 📹
- Swissmote2.0 link : https://t.me/swissmotepvbot?start=dewdrop_{dct_users[user_id]['project_name_']}

*Suggestions?* Use /suggestion."""
, parse_mode='Markdown')
                else:
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

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global dct_users
  chat_id = update.effective_chat.id
  user_id = chat_id
  candidate = search_candidate(chat_id)
  if not candidate: return
  
  # context.user_data["project"] = candidate["project_name"]

  if user_id not in dct_users:
    dct_users[user_id]={}
  
  context.user_data["assignment"] = ""
  context.user_data["assignment_image"] = []
  context.user_data["assignment_video"] = None

  context.user_data["project"] = candidate["project_name"]

  context.user_data["question"] = ""
  context.user_data["question_image"] = []
  context.user_data["question_video"] = None
  
  dct_users[user_id]['project_name'] = False
  dct_users[user_id]['listing'] = False
  dct_users[user_id]['assignment'] = False
  dct_users[user_id]['invite_message'] = False
  dct_users[user_id]['intro_message'] = False
  dct_users[user_id]['followup_2'] = False
  dct_users[user_id]['followup_4'] = False
  dct_users[user_id]['reviewer'] = False
  
  
  dct_users[user_id]['dailyupdate'] = False
  dct_users[user_id]['assignmentsubmission'] = False
  dct_users[user_id]['question'] = True
  dct_users[user_id]['candidate_login'] = False
  
  print(dct_users)
  
  await context.bot.send_message(chat_id=chat_id, text="⚠️ Remember this message will be send to Admin or leaders. Make sure it contains relevant question. \n\nAssignment is properly explained in video or text which is already provided to you\n\nWe suggest you to use AI tool like ChatGPT/Claude inorder to understand the assignment properly\n\nIf you still can't find what your looking for then start typing your question or else upload an image mentioning question within caption! We Will Help you out!")
  return

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global dct_users
  chat_id = update.effective_chat.id
  user_id = chat_id
  candidate = search_candidate(chat_id)
  if not candidate: return
  
  if candidate["daily_message"]:
    await context.bot.send_message(chat_id=chat_id, text="You can only submit one per day.", reply_markup=candidate_deafult_keyboard)
    return

  context.user_data["project"] = candidate["project_name"]
  
  # delete in handle name
  if user_id not in dct_users:
    dct_users[user_id]={}
    
  
  dct_users[user_id]['project_name'] = False
  dct_users[user_id]['listing'] = False
  dct_users[user_id]['assignment'] = False
  dct_users[user_id]['invite_message'] = False
  dct_users[user_id]['intro_message'] = False
  dct_users[user_id]['followup_2'] = False
  dct_users[user_id]['followup_4'] = False
  dct_users[user_id]['reviewer'] = False
  
  
  dct_users[user_id]['dailyupdate'] = True
  dct_users[user_id]['assignmentsubmission'] = False
  dct_users[user_id]['question'] = False
  dct_users[user_id]['candidate_login'] = False

  print(dct_users)

  await context.bot.send_message(chat_id=chat_id, text="Start typing your daily message!")
  # print("sent_day")
  return

async def assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
  global dct_users
  user_id = update.effective_chat.id
  chat_id = user_id
  # chat_id = update.effective_chat.id
  candidate = search_candidate(chat_id)
  if not candidate: return


  if user_id not in dct_users:
    dct_users[user_id]={}
    
  context.user_data["project"] = candidate["project_name"]
  
  dct_users[user_id]['project_name'] = False
  dct_users[user_id]['listing'] = False
  dct_users[user_id]['assignment'] = False
  dct_users[user_id]['invite_message'] = False
  dct_users[user_id]['intro_message'] = False
  dct_users[user_id]['followup_2'] = False
  dct_users[user_id]['followup_4'] = False
  dct_users[user_id]['reviewer'] = False
  
  
  dct_users[user_id]['dailyupdate'] = False
  dct_users[user_id]['assignmentsubmission'] = True
  dct_users[user_id]['question'] = False
  dct_users[user_id]['candidate_login'] = False

  print(dct_users)
  

  await context.bot.send_message(chat_id=chat_id, text="Start typing your assignment!")


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asyncio.create_task(background_handle_name(update, context))

#function to handle all messages that arent with a command or conversation
async def background_handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dct_users
    global unique_id_recruiter
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    name = update.effective_chat.first_name
    message = update.message.text
    print('by user: ',  message)
    print(dct_users)

    try:
        # Check if there's callback data and call reply_done
        if context.user_data.get("callback_data"):
            print('call back 1')
            await reply_done(update, context)
            return
       
        if user_id in dct_users and dct_users[user_id]['candidate_login'] == True:
          print('candidate')
          # await update.message.reply_text(text="Please enter your full name to proceed with the offer letter process. 📄✨")
          print('getttinggg.................. name')
          full_name = message
          project_split = context.user_data['project']
          await context.bot.send_message(chat_id=chat_id, text="⏳ Please wait while we process your offer letter... 📝")
          try:
            form.pdf_top(name=full_name,
              filepath=f"offer_letters/{full_name}_{project_split}_offerletter.pdf"
            )
          except:
            print('really bro')
          await context.bot.send_document(chat_id=chat_id, document=open(f"offer_letters/{full_name}_{project_split}_offerletter.pdf","rb"))
          del context.user_data['project']
          del dct_users[user_id]
        
        elif user_id in dct_users and dct_users[user_id]['project_name'] == True:
            sanitized_message = re.sub(r'\W+', '', message)
            search_result = query_get_one('''SELECT name FROM projects WHERE name = ?''', [sanitized_message])
            if search_result:
                await update.message.reply_text(text='Already have a project with the same name, \ntry some other name')
                return
            dct_users[user_id]['project_name_'] = sanitized_message
            dct_users[user_id]['project_name'] = False
            keyboard = [
                [InlineKeyboardButton("Assignment", callback_data=f'assignment_{user_id}'),
                 InlineKeyboardButton("Offer Letter", callback_data=f'offerletter_{user_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('With which process would you like to automate this listing? 📝', reply_markup=reply_markup)
            return

        elif user_id in dct_users and dct_users[user_id]['listing'] == True:
            print('listing is true')
            try:
                emp_type = dct_users[user_id]['emp_type']
                file_path = f'{emp_type}_details.txt'
                listing_num = ''
                try:
                    message = int(message)
                except ValueError:
                    await context.bot.send_message(chat_id=int(user_id), text="🔢 Message must be a number.")
                    return
                with open(file_path, 'r') as file:
                    for line in file:
                        count = line.split('___')[0]
                        if str(count) == str(message):
                            listing_num = line.split('___')[2]

                search_result = query_get_one('''SELECT listing, name, assignment FROM projects WHERE listing = ?''', [listing_num])
                if search_result is not None:
                    keyboard = [
                        [InlineKeyboardButton("Return to Listings", callback_data=f'restart_{user_id}'),
                        #  InlineKeyboardButton("Continue", callback_data=f'continue_{user_id}')]
                        ]
                    ]
                    active_project = search_result
                    # print(active_project)
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(chat_id=user_id, text=f'Already Active Project 🟢 \n\nProject Name: {active_project[1]} \nAssignment for this Listing \n\n {active_project[2]}', reply_markup=reply_markup)
                    return

                dct_users[user_id]['listing_num'] = int(listing_num)
                dct_users[user_id]['listing'] = False
                await project_name(update, context)
            except Exception as e:
                print('error in listing')
                traceback.print_exc()

        elif user_id in dct_users and dct_users[user_id]['assignment'] == True:
            try:
                process_ = 'assignment' if dct_users[user_id]['assignment_process'] else 'offer'
                
                invite_msg = await get_file_contents('messages/invite_message')
                if dct_users[user_id]['assignment_process'] == True:
                  bot_link = f"https://t.me/swissmotepvbot?start=dewdrop_{dct_users[user_id]['project_name_']}"
                else:
                  bot_link = f"https://t.me/swissmotepvbot?start=rcbwin_{dct_users[user_id]['project_name_']}"
                  
                links_to_add = bot_link + '\n' + message
                assignment_msg = await add_links_to_assignment(update, context, links=links_to_add)
                
                # add_project(listing=dct_users[user_id]['listing_num'], name=dct_users[user_id]['project_name_'],
                #             invite=dct_users[user_id]['invite_message_'], intro=dct_users[user_id]['intro_message_'],
                #             assignment=message, date=datetime.now().strftime("%Y-%m-%d"), status=1, process=process_)
                add_project(listing=dct_users[user_id]['listing_num'], name=dct_users[user_id]['project_name_'],
                            invite=invite_msg, intro=invite_msg,
                            assignment=assignment_msg, date=datetime.now().strftime("%Y-%m-%d"), status=1, process=process_)

                await followup_2(update, context)
            except Exception as e:
                traceback.print_exc()

        elif user_id in dct_users and dct_users[user_id]['invite_message'] == True:
            try:
                dct_users[user_id]['invite_message_'] = message
                # await intro_message(update, context)
                await set_invite_message(update, context, message)
                dct_users[user_id]['invite_message'] = False
                return
            except Exception as e:
                traceback.print_exc()

        elif user_id in dct_users and dct_users[user_id]['intro_message'] == True:
            try:
                dct_users[user_id]['intro_message_'] = message
                # await give_assignment(update, context)
                await set_assignment_message(update, context, message_text=message)
                dct_users[user_id]['intro_message'] = False
                return
            except Exception as e:
                traceback.print_exc()

        elif user_id in dct_users and dct_users[user_id]['followup_2'] == True:
            query_update('''UPDATE projects
                            SET followup2 = ?, followup2status = ? 
                            WHERE name = ?''', [message, 0, dct_users[user_id]['project_name_']])
            await followup_4(update, context)

        elif user_id in dct_users and dct_users[user_id]['followup_4'] == True:
            try:
                query_update('''UPDATE projects
                                SET followup4 = ?, followup4status = ? 
                                WHERE name = ?''', [message, 0, dct_users[user_id]['project_name_']])
                await context.bot.send_message(chat_id=int(user_id), text=f"""Leaders need to join from this link: https://t.me/swissmotepvbot?start=xjfysbrv_{dct_users[user_id]['project_name_']}""")
                asyncio.create_task(execute_internshala_automation(update, context))
            except Exception as e:
                traceback.print_exc()
        
        elif user_id in dct_users and dct_users[user_id]['assignmentsubmission'] == True:
                   
            # chat_id = update.effective_chat.id
            # assignment_message = update.message.text

            # if len(assignment_message) < 50:
            #   await context.bot.send_message(chat_id=update.effective_chat.id, text="Your assignment should contain at least 50 characters, Enter again!")
            #   return

            # name = update.effective_chat.first_name
            # project = context.user_data["project"]

            # message = f"✅ Assignment received from {name}, for the project: {project}." + "\n\n" + \
            # f"{assignment_message}"

            
            
            # leaders = get_leaders(project)
            # for leader in leaders:
            #   await context.bot.send_message(chat_id=leader["chat_id"], text=message, parse_mode='Markdown', 
            #   reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "as", "u": chat_id, "m":[]}))]]))
            
            # await context.bot.send_message(chat_id=chat_id, text="📝 Your assignment was successfully submitted and will be reviewed by the leadership team. Thank you!", reply_markup=candidate_deafult_keyboard)
            # dct_users[user_id]['assignmentsubmission'] = False
            # return
          
            if update.message.text:
                assignment = update.message.text.strip()
                context.user_data["assignment"] = assignment
                if len(assignment) < 20:
                  await context.bot.send_message(chat_id=update.effective_chat.id, text="Your assignment should contain at least 50 characters, Enter again!")
                  return
                
            # Check if the message contains a photo and a caption
            elif update.message.photo and update.message.caption:
              
                media = update.message.photo
                if not media:
                  media = update.message.document

                context.user_data["assignment_image"].append(media)
                
                
                assignment = update.message.caption.strip()
                context.user_data["assignment"] = assignment

            elif update.message.video and update.message.caption:
              
                if not media:
                  media = update.message.document

                context.user_data["assignment_video"] = media
                
                
                assignment = update.message.caption.strip()
                context.user_data["assignment"] = assignment
                
                
            
            message = context.user_data["assignment"]
            project = context.user_data["project"]

            leaders = get_leaders(project)
            for leader in leaders:
              message_id = []
              for img in context.user_data["assignment_image"]:
                if isinstance(img, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=img)
                else: media = await context.bot.send_photo(chat_id=leader["chat_id"],photo=img[-1])
                
                message_id.append(media.message_id)
                
                vid = context.user_data["assignment_video"] 
                if vid is not None:
                  if isinstance(vid, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=vid)
                  else: media = await context.bot.send_video(chat_id=leader["chat_id"],video=vid[-1])

                  message_id.append(media.message_id)

              await context.bot.send_message(chat_id=leader["chat_id"],
                text=f"✅ assignment received from {name}, for the project: {project}.\n\n{message}", parse_mode='Markdown', 
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "as", "u": chat_id, "m":[]}))]]))

            
            
            await context.bot.send_message(chat_id=chat_id, text="📚 Your assignment has been successfully submitted and will get back to you!")
            dct_users[user_id]['assignment'] = False
            del dct_users[user_id]
            return

        elif user_id in dct_users and dct_users[user_id]['question'] == True:

            if update.message.text:
                question = update.message.text.strip()
                context.user_data["question"] = question

                if len(question) < 10:
                  await context.bot.send_message(chat_id=update.effective_chat.id, text="Your question should contain at least 40 characters,\n Enter again!")
                  return
                
            # Check if the message contains a photo and a caption
            elif update.message.photo and update.message.caption:
              
                media = update.message.photo
                if not media:
                  media = update.message.document

                context.user_data["question_image"].append(media)
                
                
                question = update.message.caption.strip()
                context.user_data["question"] = question
            elif update.message.video and update.message.caption:
              
                if not media:
                  media = update.message.document

                context.user_data["question_video"] = media
                
                
                question = update.message.caption.strip()
                context.user_data["question"] = question
                
                
            
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

            
            
            await context.bot.send_message(chat_id=chat_id, text="📚 Your Question has been successfully submitted and will get back to you!")
            dct_users[user_id]['question'] = False
            del dct_users[user_id]
            return
          
        elif user_id in dct_users and dct_users[user_id]['dailyupdate'] == True:
            try:
              chat_id = update.effective_chat.id
              daily_message = update.message.text.strip()
              print("daily_message")

              if len(daily_message) < 100:
                await context.bot.send_message(chat_id=chat_id, text="Your daily message should contain at least 100 characters,\nEnter again!")
                return
              
              # name = update.effective_chat.first_name
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
              dct_users[user_id]['dailyupdate'] = False
              del dct_users[user_id]
              
              return
            
            except Exception as e:
              print(e)
 
        # TODO fix LLM
        else:
            print('inside LLM code ')
            if search_leader(chat_id):
              print('you are leader') 
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
              # pass url(regex) candidate database
              print('inside else query')
              assignment_text = query_get_one('''SELECT p.assignment
              FROM candidates c
              JOIN projects p ON c.project_name = p.name
              WHERE c.chat_id = ?;''', [chat_id])
              print(len(assignment_text['assignment']))

              # helper.give_answer(url="" ,query=message)
    except:
      print('error in background handle name')
      traceback.print_exc()
      pass
   
async def set_invite_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text:str=""):
  # make_folders(["messages"])
  file_path = Path("messages/invite_message")
  async with aiofiles.open(file_path, mode='w') as file:
        await file.write(message_text)

  # Send a confirmation message to the user (optional)
  await update.message.reply_text("Invite message has been set.")
   
async def set_assignment_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text:str=""):
  # make_folders(["messages"])
  file_path = Path("messages/assignment_message")
  async with aiofiles.open(file_path, mode='w', encoding='utf-8') as file:
        await file.write(message_text)

  # Send a confirmation message to the user (optional)
  await update.message.reply_text("Assignment message has been set.")
  
async def get_file_contents(file_path: str) -> str:
    file = Path(file_path)

    if not file.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    async with aiofiles.open(file_path, mode='r') as file:
        contents = await file.read()

    return contents
  
async def add_links_to_assignment(update: Update, context: ContextTypes.DEFAULT_TYPE, links:str):
  try:
    assignment_contents = await get_file_contents('messages/assignment_message')
    placeholder = 'xx_link_xx'
    updated_contents = assignment_contents.replace(placeholder, links)
        
    await update.message.reply_text("Links have been added to the assignment.")
    return updated_contents
  except FileNotFoundError as e:
    print('error')
    # await update.message.reply_text(str(e))  
 
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
    
    print('background_execute_internshala_automation')
    print(len(dct_users))
    print(dct_users)
    # FIND intershala_automation_start_api
    print('intershala_automation_start_api.py')
    # success = await run_async_process_mk(['intershala_automation_start_api.py', str(listing_number)])
    success = True
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
    print("\n\n\n", query, "\n\n\n")
    Query_called = query.data.strip().split("_")
    print(Query_called[0])
    user_id = query.from_user.id
        
    print(query.data)
    print('🟥'*3)
    # Check for reply callback data
    try:
      callback_data = json.loads(query.data)
      context.user_data["callback_data"] = callback_data
           
      # FIND REPLY
      if callback_data["t"] == "d":
        context.user_data["reply"] = "Daily"
        await context.bot.send_message(chat_id=user_id, text="📝 Enter reply to the daily message:")

      elif callback_data["t"] == "q":
        context.user_data["reply"] = "Question"
        context.user_data["callback_data"]["m"].append(update.effective_message.id)
        await context.bot.send_message(chat_id=user_id, text="📝 Enter reply to the question:")

      elif callback_data["t"] == "as":
        context.user_data["reply"] = "Assignment"
        await context.bot.send_message(chat_id=user_id, text="📝 Enter reply to the assignment:")

      elif callback_data["t"] == "an":
        context.user_data["reply"] = "Announce"
        context.user_data["project"] = callback_data["p"]
        await context.bot.send_message(chat_id=user_id, text="Start typing the announcement:")

      elif callback_data["t"] == "itnan":
        context.user_data["reply"] = "Internshala_Announce"
        context.user_data["project"] = callback_data["p"]
        await context.bot.send_message(chat_id=user_id, text="Start typing the Internshala announcement:")

      elif callback_data["t"] == "glban":
        context.user_data["reply"] = "Global_Announce"
        # context.user_data["project"] = callback_data["p"]
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(chat_id=user_id, text="Start typing the Global announcement:")

    except:
      print('callback not in json format')
      
    # Handle other query actions
    if user_id in dct_users:           
      if Query_called[0] == 'assignment':
        await query.edit_message_text(text="✅ Assignment process...")
        dct_users[user_id]['assignment_process'] = True
        # asyncio.create_task(invite_message(update, context))
        asyncio.create_task(give_assignment(update, context))

      elif Query_called[0] == 'offerletter':
        await query.edit_message_text(text="✅ Offer letter process...")
        dct_users[user_id]['assignment_process'] = False
        # asyncio.create_task(invite_message(update, context))
        asyncio.create_task(give_assignment(update, context))

      elif Query_called[0] == 'create':
        await query.edit_message_text(text="🔧 Currently in Testing phase. Will be Live soon.")

      elif Query_called[0] == 'choose' or Query_called[0] == 'restart':
        keyboard = [
          [InlineKeyboardButton("Internship", callback_data=f'emp_itn_{user_id}'),
          InlineKeyboardButton("Jobs", callback_data=f'emp_job_{user_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="👉 Proceed to choose an existing listing.", reply_markup=reply_markup)
      
      elif Query_called[0] == 'active':
        await query.edit_message_text(text="👉 All Active Projects ", reply_markup=None)
        await get_projects(update, context, 1)
        
      elif Query_called[0] == 'close':
        await query.edit_message_text(text="👉 All Closed Projects ", reply_markup=None)
        await get_projects(update, context, 0)
        
      elif Query_called[0] == 'emp' and Query_called[1] == 'itn':
        asyncio.create_task(choose_listing_automate(update, context, 1, 1, "internship"))
        return 0
                
      elif Query_called[0] == 'emp' and Query_called[1] == 'job':
        asyncio.create_task(choose_listing_automate(update, context, 1, 1, "job"))
        return 0
                
      elif Query_called[0] == 'next':
        asyncio.create_task(choose_listing_automate(update, context, 1, Query_called[1], Query_called[2]))
      
      elif Query_called[0] == "closeproject":
        await query.edit_message_text(text='☠')
        query_update(f'''UPDATE projects SET status = ?  WHERE listing = ? ''', (0, Query_called[1]) )
        print(Query_called[1])
        # sleep(3)
        # await query.edit_message_text(text='Project Deleted successfully')

      elif Query_called[0] == "setinvite":
        await query.edit_message_text(text='📝')
        asyncio.create_task(invite_message(update, context))

      elif Query_called[0] == "setassignment":
        await query.edit_message_text(text='📚')
        asyncio.create_task(intro_message(update, context))
      
      elif Query_called[0] == 'getmessages':
        invite_msg = await get_file_contents('messages/invite_message')
        assignment_msg = await get_file_contents('messages/assignment_message')

        await query.edit_message_text('📖')
        await context.bot.send_message(chat_id=user_id, text=f'**Invite Message** '\
                                       f"``` {invite_msg} ```", parse_mode='Markdown')
        await context.bot.send_message(chat_id=user_id, text=f'**Assignment Message** '\
                                       f"``` {assignment_msg} ```", parse_mode='Markdown')
        
      elif Query_called[0] == 'makeannouncement':
        keyboard = [
          [InlineKeyboardButton("Make Announcement", callback_data=f'telan_{user_id}')],
          [InlineKeyboardButton("Make Announcement on Internshala", callback_data=f'itnan_{user_id}')],
          [InlineKeyboardButton("Global Message", callback_data=json.dumps({"t": "glban", "p": 'all'}))]
          # reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=json.dumps({"t": "an", "p": p["project_name"]}))])
          ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Announcement 📢", reply_markup=reply_markup)
      elif Query_called[0] == 'telan':
        await query.edit_message_reply_markup(reply_markup=None)
        await announcement(update, context)
        
      elif Query_called[0] == 'itnan':
        await query.edit_message_reply_markup(reply_markup=None)
        await announce_internshala(update, context)
      
      elif Query_called[0] == 'glban':
        await announce_global(update, context)
      
      else:
        if Query_called[0] == 'announce':
          print('project mk: ')
          print(Query_called[1])
          await context.bot.send_message(chat_id=user_id, text=f"Write announcement for {Query_called[1]}")
          await get_announcement(update, context, Query_called[2]) 
  except Exception as e:
    traceback.print_exc()
    await context.bot.send_message(update.effective_user.id, f"❌ Operation compromised. Please try again.")
    return
    
async def get_projects(update: Update, context: ContextTypes.DEFAULT_TYPE, status: int):
  user_id = update.effective_user.id
  all_active_projects = query_get_many(f'''SELECT * FROM projects WHERE status = {status}''')
  if not all_active_projects:
      await context.bot.send_message(chat_id=user_id, text='No listings found')
      print("Add some listings....")
      return
  for project in all_active_projects:
    if status == 1:
      reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"❌ Close", callback_data=f"closeproject_{project['listing']}")]]
      )
    else:
      reply_markup = None
      
    await context.bot.send_message(chat_id=user_id, text=f"Project Name: {project['name']}\n" \
                                                          f"\nProcess: {project['process']}\n" \
                                                          f"\nDate: {project['date']}\n",
                                                          reply_markup=reply_markup)
    
async def announce_internshala(update: Update, context:ContextTypes.DEFAULT_TYPE):
  print('announce_internshala')
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
      reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=json.dumps({"t": "itnan", "p": p["project_name"]}))])
    await context.bot.send_message(chat_id=chat_id, text=f"Select a project to announce in", 
    reply_markup = InlineKeyboardMarkup(reply_markup))
    cursor.close()
    return
  else:
    context.bot.send_message(chat_id=chat_id, text="Only Leaders with active projects have access to this command")

async def announce_global(update: Update, context:ContextTypes.DEFAULT_TYPE):
  print('global_announce')
  chat_id = update.effective_chat.id
  leader = search_leader(chat_id)
  if not leader:
    await context.bot.send_message(chat_id=chat_id, text="Only Leaders have access to this command")
    return
  
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM leaders WHERE chat_id = {chat_id};')
  projects = cursor.fetchall()
  if projects:
    # reply_markup=[]
    # for p in projects:
    #   reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=json.dumps({"t": "itnan", "p": p["project_name"]}))])
    # reply_markup = InlineKeyboardMarkup(reply_markup))
    global_announce = await context.bot.send_message(chat_id=chat_id, text=f"Started the process of global announcement")
    cursor.close()
    return
  else:
    context.bot.send_message(chat_id=chat_id, text="Only Leaders with active projects have access to this command")
    
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


async def forever_checking_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  while True:
    print("we here")
    # ALL ACTIVE projects ACTIVE => status = 1
    all_projects = query_get_many('''SELECT * FROM projects WHERE status = 1''')
    # print(len(all_projects))
    if not all_projects:
      await context.bot.send_message(chat_id=user_id, text='No listings found')
      print("Add some listings....")
      return
    
    curr_date = datetime.now().strftime("%Y-%m-%d")
    for project in all_projects:
      # FIND intershala_automation_start_api
      print('intershala_automation_start_api.py')
      # success = await run_async_process_mk(['intershala_automation_start_api.py', str(project['listing'])])
      success = True
      if not success:
        send_email("Fail","Fail forever")
        return

      if project['followup2'] == '' and  project['followup4'] == '':
        continue
      if project['followup2status'] == 1 and project['followup4status'] == 1:
        continue
      
      # print('success', success)
      # project['followup2'], project['followup2status'], project['followup4'], project['followup4status'])
      # for col in project:
      #   print(col, end = " | ")
      # print()
      # if follow up day 2 AND followup2 != '' AND followup2status == 0(inactive)
      if days_between(curr_date, project['date']) == 2 and project['followup2status'] == 0 and project['followup2'] != '':
        # send follow up 2 and update status
        try:
          ids = await get_all_shortlisted_applicants(listing_num=str(project['listing']))
          asyncio.create_task(send_message_using_id(ids=ids, message=project['followup2'], listing_num=str(project['listing'])))
          query_update('''UPDATE projects SET followup2status = 1 WHERE name = ?''', project['name'])
        except:
          print('Error while sending Follow up 2')
          # send_email("Fail","Fail forever")
          traceback.print_exc


      # if follow up day 4 AND followup4 != '' AND followup4status == 0(inactive)
      if days_between(curr_date, project['date']) == 4 and project['followup4status'] == 0 and project['followup4'] != '':
        # send follow up 4 and update status
        try:
          ids = await get_all_shortlisted_applicants(listing_num=str(project['listing']))
          asyncio.create_task(send_message_using_id(ids=ids, message=project['followup4'], listing_num=str(project['listing'])))
          query_update('''UPDATE projects SET followup4status = 1 WHERE name = ?''', project['name'])
        except:
          print('Error while sending Follow up 2')
          # send_email("Fail","Fail forever")
          traceback.print_exc
      
    await asyncio.sleep(14400)  # 4 hours in seconds
    
    


async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    asyncio.create_task(forever_checking_status(update, context))
    

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
      reply_markup.append([InlineKeyboardButton(p["project_name"], callback_data=json.dumps({"t": "an", "p": p["project_name"]}))])
    await context.bot.send_message(chat_id=chat_id, text=f"Select a project to announce in", 
    reply_markup = InlineKeyboardMarkup(reply_markup))
    cursor.close()
    return
  else:
    context.bot.send_message(chat_id=chat_id, text="Only Leaders with active projects have access to this command")

async def get_announcement(update:Update, context: ContextTypes.DEFAULT_TYPE, chat_id):
  await context.bot.send_message(chat_id=chat_id, text="Enter announcement")
  return 6

async def announcement_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message = update.message.text
  print(message)
  return ConversationHandler.END

# async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   chat_id = update.effective_chat.id

#   candidate = search_candidate(chat_id)
#   if not candidate: return

#   if candidate["daily_message"]:
#     await context.bot.send_message(chat_id=chat_id, text="You can only submit one per day.", reply_markup=candidate_deafult_keyboard)
#     return ConversationHandler.END

#   context.user_data["project"] = candidate["project_name"]

#   await context.bot.send_message(chat_id=chat_id, text="Start typing your daily message!", reply_markup=candidate_deafult_keyboard)
#   print("sent_day")
#   return 0

# async def daily_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   try:
#     chat_id = update.effective_chat.id
#     daily_message = update.message.text.strip()
#     print("daily_message")

#     if len(daily_message) < 100:
#       await context.bot.send_message(chat_id=chat_id, text="Your daily message should contain at least 100 characters,\nclick /daily to Try again!", reply_markup=candidate_deafult_keyboard)
#       return 0
    
#     name = update.effective_chat.first_name
#     daily_message = update.message.text
#     project = context.user_data["project"]

#     message = f"✅ Daily Update received from {name}, for the project: {project}." + "\n\n" + \
#     f"{daily_message}"

#     leaders = get_leaders(project)
#     for leader in leaders:
#       await context.bot.send_message(chat_id=leader["chat_id"], text=message, parse_mode='Markdown', 
#       reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "d", "u": chat_id, "m":[]}))]]))
    
#     update_candidate(chat_id, daily_counter = 0, daily_message = True)

#     await context.bot.send_message(chat_id=chat_id, text="📝 Your daily update has been successfully submitted and will be reviewed by the leadership team. Thank you!", reply_markup=candidate_deafult_keyboard)

#     return ConversationHandler.END
#   except Exception as e:
#      print(e)

question_keyboard = ReplyKeyboardMarkup(
  [["Attach Image", "Attach Video", "Submit", "Cancel"]],
  one_time_keyboard=True,
  input_field_placeholder="Attach/Submit/Cancel?"
)

# async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   chat_id = update.effective_chat.id

#   candidate = search_candidate(chat_id)
#   if not candidate: return

#   context.user_data["project"] = candidate["project_name"]

#   context.user_data["question"] = ""
#   context.user_data["question_image"] = []
#   context.user_data["question_video"] = None

#   await context.bot.send_message(chat_id=chat_id, text="⚠️ Remember this message will be send to Admin or leaders. Make sure it contains relevant question. \n\nAssignment is properly explained in video or text which is already provided to you\n\nWe suggest you to use AI tool like ChatGPT/Claude inorder to understand the assignment properly\n\nIf you still can't find what your looking for then start typing your question! We Will Help you out!", reply_markup=ReplyKeyboardRemove())
#   return 1

# # 0
# async def question_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   question = update.message.text.strip()

#   if len(question) < 40:
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Your question should contain at least 40 characters,\nTry again!", reply_markup=candidate_deafult_keyboard)
#     return 1
  
#   context.user_data["question"] = question
#   await update.message.reply_text(f"Choose an option: ", reply_markup=question_keyboard)
  
#   return 2

# # 1
# async def question_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   chat_id = update.effective_chat.id
#   name = update.effective_chat.first_name

#   if update.message.text.lower() == "attach image":
#     if len(context.user_data["question_image"]) >= 3:
#       await context.bot.send_message(chat_id=chat_id, text="Cannot attach more than 3 pictures", reply_markup=question_keyboard)
#       return 2

#     await context.bot.send_message(chat_id=chat_id, text="Send one picture at a time. (max 3)", reply_markup=ReplyKeyboardRemove())
#     return 3
#   elif update.message.text.lower() == "attach video":
#     if context.user_data["question_video"] is not None:
#       await context.bot.send_message(chat_id=chat_id, text="Cannot attach more than 1 video", reply_markup=question_keyboard)
#       return 2

#     await context.bot.send_message(chat_id=chat_id, text="Send one video at a time. (max 1)", reply_markup=ReplyKeyboardRemove())
#     return 4
#   elif update.message.text.lower() == "submit":
#     message = context.user_data["question"]
#     project = context.user_data["project"]

#     leaders = get_leaders(project)
#     for leader in leaders:
#       message_id = []
#       for img in context.user_data["question_image"]:
#         if isinstance(img, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=img)
#         else: media = await context.bot.send_photo(chat_id=leader["chat_id"],photo=img[-1])
        
#         message_id.append(media.message_id)
        
#         vid = context.user_data["question_video"] 
#         if vid is not None:
#           if isinstance(vid, Document): media = await context.bot.send_document(chat_id=leader["chat_id"],document=vid)
#           else: media = await context.bot.send_video(chat_id=leader["chat_id"],video=vid[-1])

#           message_id.append(media.message_id)

#       await context.bot.send_message(chat_id=leader["chat_id"],
#         text=f"✅ Question received from {name}, for the project: {project}.\n\n{message}", parse_mode='Markdown', 
#         reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "q", "u": chat_id, "m":message_id}))]]))

#     await context.bot.send_message(chat_id=chat_id, text="📚 Your Question has been successfully submitted and will get back to you!", reply_markup=candidate_deafult_keyboard)
#   elif update.message.text.lower() == "cancel":
#     await context.bot.send_message(chat_id=chat_id, text="Operation canceled, try again?", reply_markup=candidate_deafult_keyboard)
  
#   return ConversationHandler.END

# # 2
# async def question_attach_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   media = update.message.photo
#   if not media:
#     media = update.message.document

#   context.user_data["question_image"].append(media)

#   await update.message.reply_text(f"Image attached, choose another option!", reply_markup=question_keyboard)
#   return 2

# # 3
# async def question_attach_vid(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   media = update.message.video
#   if not media:
#     media = update.message.document

#   context.user_data["question_video"] = media

#   await update.message.reply_text(f"Video attached, choose another option!", reply_markup=question_keyboard)
#   return 2

# async def assignment(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   chat_id = update.effective_chat.id
#   candidate = search_candidate(chat_id)
#   if not candidate: return

#   context.user_data["project"] = candidate["project_name"]

#   await context.bot.send_message(chat_id=chat_id, text="Start typing your assignment!")
#   return 5

# async def assignment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   chat_id = update.effective_chat.id
#   assignment_message = update.message.text

#   if len(assignment_message) < 80:
#     await context.bot.send_message(chat_id=update.effective_chat.id, text="Your assignment should contain at least 80 characters,\nClick /assignment to Try again!", reply_markup=candidate_deafult_keyboard)
#     return 5

#   name = update.effective_chat.first_name
#   project = context.user_data["project"]

#   message = f"✅ Assignment received from {name}, for the project: {project}." + "\n\n" + \
#   f"{assignment_message}"

#   leaders = get_leaders(project)
#   for leader in leaders:
#     await context.bot.send_message(chat_id=leader["chat_id"], text=message, parse_mode='Markdown', 
#     reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Reply", callback_data=json.dumps({"t": "as", "u": chat_id, "m":[]}))]]))
  
#   await context.bot.send_message(chat_id=chat_id, text="📝 Your assignment was successfully submitted and will be reviewed by the leadership team. Thank you!", reply_markup=candidate_deafult_keyboard)

#   return ConversationHandler.END

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

  elif callback_data["t"] == "itnan":
    context.user_data["reply"] = "Internshala_Announce"
    context.user_data["project"] = callback_data["p"]
    await context.bot.send_message(chat_id=chat_id, text="Start typing the announcement:")

async def reply_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
  print('inside reply done')
  print('📞'*3)
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
      # print('inside for looop')
      # print('index: ', index)
      if index % 10 == 0: 
        await announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
      try:
        await context.bot.send_message(chat_id=candidate["chat_id"], text=f"Message from Team: \n{message}")
      except Exception as e:
        print(e)

    # announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
    await update.message.reply_text(f"☑️ Announcement done.")

  elif context.user_data["reply"] == "Internshala_Announce":
    message = update.message.text
    project = context.user_data["project"]

    print('project: ', project)
    try:
      project_listing = query_get_one('''SELECT listing
                                    FROM projects
                                    WHERE name = ?
                                    ''', [project])['listing']
    except:
      await context.bot.send_message(chat_id=user_id, text=f"⚡ alot of traffic over server")
      print('error while sending internshala announcement')
      traceback.print_exc()
      
    print(project_listing)
    print(type(project_listing))
    try:
      ids = await get_all_shortlisted_applicants(listing_num=project_listing)
      # TODO comment print and uncomment create_task
      print(len(ids))
      # asyncio.create_task(send_message_using_id(ids=ids, message=project['followup2'], listing_num=str(project['listing'])))
    except:
      print('Error while sending message over internshala')
      # send_email("Fail","Fail forever")
      traceback.print_exc
    
    # announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
    await update.message.reply_text(f"☑️ Announcement done.")

    del context.user_data["project"]
    
  #TODO  check it before merge
  elif context.user_data["reply"] == "Global_Announce":
    print('Global Announce')
    message = update.message.text

    try:
      all_projects = query_get_many('''SELECT listing, name
                                    FROM projects
                                    ''')
    except:
      await context.bot.send_message(chat_id=user_id, text=f"⚡ alot of traffic over server")
      print('error while sending Global announcement')
      traceback.print_exc()
      
    project_listing = {}  
    # print(all_projects)
    # print(type(all_projects))
    for listing, name in all_projects:
      project_listing[name] = listing

    print(project_listing)
    announce_stat = await update.message.reply_text(f"🔄 Processing announcement.")
    for project in project_listing:
      await announce_stat.edit_text(f"🔄 Processing announcement. \nProject: {project}")
      candidates = get_candidates(project)
      print(candidates.__len__())
      # print(project, project_listing[project])
      for candidate in candidates:
        try:
          await context.bot.send_message(chat_id=candidate["chat_id"], text=f"Message from Team: \n{message}")
        except Exception as e:
          print(e)
      await update.message.reply_text(f"☑️ Announcement done.")

      # print('sleeping for 3 secs')
      # sleep(3)
      for candidate in candidates:
        try:
          ids = await get_all_shortlisted_applicants(listing_num=project_listing[project])
          if ids[0] == False:
            print('broken', ids[1])
            return
          # TODO comment print and uncomment create_task
          print("total candidates :",len(ids))
          # asyncio.create_task(send_message_using_id(ids=ids, message=project['followup2'], listing_num=str(project['listing'])))
        except:
          print('Error while sending message over internshala')
          # send_email("Fail","Fail forever")
          traceback.print_exc
      await update.message.reply_text(f"☑️ Announcement done over internshala.")
    
    # announce_stat.edit_text(f"🔄 Processing announcement. [{index}/{total}]")
    # await update.message.reply_text(f"☑️ Announcement done.")

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

def make_folders(dir_names:list):
  for name in dir_names:
    try:
      os.makedirs(name, exist_ok=True)
    except Exception as e:
      print(f'error occured while making directory {name}', e)

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.effective_chat.id
  print('getttinggg.................. name')
  full_name = update.message.text
  print('full_name: ', full_name)
  project_split = context.user_data['project']
  await context.bot.send_message(chat_id=chat_id, text="⏳ Please wait while we process your offer letter... 📝")

  try:
    form.pdf_top(name=full_name,
      filepath=f"offer_letters/{full_name}_{project_split}_offerletter.pdf"
    )
  except:
    print('really bro')
            
  # await context.bot.send_document(chat_id=chat_id, document=open(f"offer_letters/{full_name}_{project_split}_offerletter.pdf","rb"))
  await context.bot.send_message(chat_id=chat_id, text="GOoopd")
  del context.user_data['project']

  return ConversationHandler.END


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

    app.add_handler(CommandHandler("question", question))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("assignment", assignment))

    # try:
    #   app.add_handler(ConversationHandler(
    #       entry_points=[CommandHandler("daily", daily)],
    #       states={
    #       0 : [MessageHandler(filters.TEXT & ~filters.COMMAND, daily_message)],
    #       },
    #       fallbacks=[MessageHandler(filters.COMMAND, ignore)],
    #   ))
    # except Exception as e:
    #    print(e)
    
    # app.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler("question", question)],
    #     states={
    #     1: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_message)],
    #     2: [MessageHandler(filters.TEXT & ~filters.COMMAND, question_select)],
    #     3: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, question_attach_img)],
    #     4: [MessageHandler(filters.VIDEO | filters.Document.VIDEO, question_attach_vid)],
    #     },
    #     fallbacks=[MessageHandler(filters.COMMAND, ignore)],
    # ))

    # app.add_handler(ConversationHandler(
    #     entry_points=[CommandHandler("assignment", assignment)],
    #     states={
    #     5: [MessageHandler(filters.TEXT & ~filters.COMMAND, assignment_message)],
    #     },
    #     fallbacks=[MessageHandler(filters.COMMAND, ignore)],
    # ))
    
    app.add_handler(ConversationHandler(
      entry_points=[CommandHandler("offer", initiate_offerletter)],
      states={
        6: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_fullname)]
      },
      fallbacks=[MessageHandler(filters.COMMAND, ignore)]
    ))
    
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_done))
    
    print("Initializing update checks")

    # TODO Uncomment
    # app.job_queue.run_repeating(check_updates, 3600)
    # app.job_queue.run_repeating(run, 3600)

    print("Polling...")
    main_event_loop = asyncio.get_event_loop()
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == '__main__':
    make_folders(['listings', 'offer_letters', 'messages'])
    main_loop = asyncio.run(main())
 