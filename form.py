from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
# COMMENTED OUT assignment and link for bot

#write onto existing pdf pages
def get_page_write(i,name): #,rep,des, link): #,assign,link):
    #### page 2
    if i==2:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Times-Roman", 11)
        can.drawString(158, 156, name)
        can.drawString(156,143, str(datetime.now().date()))
        can.save()
        packet.seek(0)
        return packet


    ###### page 0
    if i==0:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Times-Roman", 11)
        can.drawString(109, 777, name)
        can.drawString(101, 675, str(datetime.now().date()))
        # can.drawString(145, 632, rep)
        # can.drawString(145, 645, des)
        can.save()
        packet.seek(0)
        return packet

    ##### page 3
    if i==3:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Times-Roman", 11)
        # can.drawString(80,784, str(datetime.now().date()))
        # can.drawString(190, 725, assign)
        # can.drawString(222, 635, link)
        # can.drawString(200, 559, "Join the Telegram group using the above link to know more.")
        can.save()
        packet.seek(0)
        return packet

def pdf_top(name, filepath):
    # Read your existing PDF
    print('started process')
    existing_pdf = PdfReader(open("form.pdf", "rb"))

    # Create an output PDF
    output = PdfWriter()
    for i in range(4):
        packet=get_page_write(i,name) #,rep,des,link) #assign,link)
        if not packet:
            continue
        new_pdf = PdfReader(packet)
        page = existing_pdf.pages[i]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
    print('outpppppttttt')
    # Write the output to a new file
    with open(filepath, "wb") as output_stream:
        print('writing output')
        output.write(output_stream)
        
    print('good to go 🚗🌪')
