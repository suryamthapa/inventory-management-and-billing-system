from frontend.utils import nepali_datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, \
     NextPageTemplate, Paragraph, Table, TableStyle, Spacer


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._codes = []
    
    def showPage(self):
        self._codes.append({'code': self._code, 'stack': self._codeStack})
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        # reset page counter
        self._pageNumber = 0
        for code in self._codes:
            # recall saved page
            self._code = code['code']
            self._codeStack = code['stack']
            self.setFont("Helvetica", 12)
            # doc.page_width - 2.6*self.rightMargin, doc.page_height - 1.5 * self.topMargin
            self.drawString(letter[0] - 2.83*inch, letter[1] - 0.8 * inch, f"Page no   :  {self._pageNumber+1} of {len(self._codes)}")
            canvas.Canvas.showPage(self)
        self._doc.SaveToFile(self._filename, self)


class CustomerLedger(BaseDocTemplate):
    def __init__(self, filename, company_info, ledger_details, **kwargs):
        super().__init__(filename, page_size=letter, _pageBreakQuick=0, **kwargs)
        self.company_info = company_info
        self.ledger_details = ledger_details
        self._pages_created = 0

        self.page_width = (self.width + self.leftMargin * 2)
        self.page_height = (self.height + self.bottomMargin * 2)
        # self.leftMargin = 0.8*inch

        styles = getSampleStyleSheet()
        # Setting up the frames, frames are use for dynamic content not fixed page elements
        first_page_table_frame = Frame(self.leftMargin, 1.7*self.bottomMargin, self.width, self.height - 2.6 * inch, id='small_table')
        later_pages_table_frame = Frame(self.leftMargin, 1.7*self.bottomMargin, self.width, self.height - 2.6 * inch, id='large_table')

        # Creating the page templates
        first_page = PageTemplate(id='FirstPage', frames=[first_page_table_frame], onPage=self.on_first_page)
        later_pages = PageTemplate(id='LaterPages', frames=[later_pages_table_frame], onPage=self.add_default_info)
        self.addPageTemplates([first_page, later_pages])

        # Tell Reportlab to use the other template on the later pages,
        # by the default the first template that was added is used for the first page.
        story = [NextPageTemplate(['*', 'LaterPages'])]

        data = self.get_data_for_table()

        table_style = []
        for i in range(1, len(data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND',(0,i),(-1,i),colors.whitesmoke))
            else:
                table_style.append(('BACKGROUND',(0,i),(-1,i),colors.white))
        
        dr_amount = self.ledger_details["summary"]["dr_amount"]
        cr_amount = self.ledger_details["summary"]["cr_amount"]
        account_balance = self.ledger_details["summary"]["account_balance"]
        data += [["", "", "Total:", 
                "{:,.2f}".format(float(dr_amount)), 
                "{:,.2f}".format(float(cr_amount)), 
                f"{account_balance}"]]
        data += [["", "", "Ledger Total:", 
                "{:,.2f}".format(float(dr_amount)), 
                "{:,.2f}".format(float(cr_amount)), 
                f"{account_balance}"]]

        tableMainStyle = TableStyle([
                                ("BOX",(0,0),(5,0),0.1,colors.black),
                                ("LINEAFTER",(0,0),(0,0),0.1,colors.black),
                                ("LINEAFTER",(1,0),(1,0),0.1,colors.black),
                                ("LINEAFTER",(2,0),(2,0),0.1,colors.black),
                                ("LINEAFTER",(3,0),(3,0),0.1,colors.black),
                                ("LINEAFTER",(4,0),(4,0),0.1,colors.black),
                                ("BACKGROUND",(0,0),(5,0),colors.whitesmoke),
                                ("FONT",(0,0),(5,0),"Helvetica-Bold",10),
                                ("FONT",(0,-1),(-1,-1),"Helvetica-Bold",10),
                                ("FONT",(0,-2),(-1,-2),"Helvetica-Bold",10),
                                ("ALIGN",(-4,-1),(-4,-1),"RIGHT"),
                                ("ALIGN",(-4,-2),(-4,-2),"RIGHT"),
                                ("NOSPLIT",(-1,-3),(-1,-1))
                            ] + table_style)

        story.append(Table(data, repeatRows=1, colWidths=[0.4*inch, inch, inch*2, 1*inch, 1*inch, 1.3*inch],
                           style=tableMainStyle, splitByRow=1))

        self.build(story, canvasmaker=NumberedCanvas)
        # self.draw_page_number(canvas, doc)

    def get_data_for_table(self):
        headings = ["S.N.", "Date", "Account Description", "Debit", "Credit", "Balance"]
        rows = []
        # totalProductsInBill = len(self.ledger_details.get("account"))
        for index, details in enumerate(self.ledger_details["account"]):
            rows.append([str(index+1), 
                        str(details["date"]), 
                        Paragraph(str(details["description"])),
                        "{:,.2f}".format(float(details.get("amount"))) if details.get("type") == "debit" else " ",
                        "{:,.2f}".format(float(details.get("amount"))) if details.get("type") == "credit" else " ",
                        details.get("account_balance")])
        return [headings] + rows

    def draw_page_number(self, canvas, doc):

        pass
    def on_first_page(self, canvas, doc):
        canvas.saveState()
        # Add the logo and other default stuff
        self.add_default_info(canvas, doc)
        canvas.restoreState()

    def add_default_info(self, canvas, doc):
        canvas.saveState()
        # company name
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 1 * self.topMargin, f"{self.company_info.get('company_name')}")
        
        # additinonal info
        canvas.setFont("Helvetica", 12)
        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 1.3 * self.topMargin, f"PAN no: {self.company_info.get('pan_no')}")
        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 1.5 * self.topMargin, f"{self.company_info.get('municipality')} {self.company_info.get('ward')}, {self.company_info.get('district')}, {self.company_info.get('province')}, {self.company_info.get('country')}")

        phone_num = self.company_info.get('phone_number')
        telephone = self.company_info.get('telephone')
        contacts = []
        if phone_num: contacts.append(phone_num) 
        if telephone: contacts.append(telephone) 
        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 1.7 * self.topMargin, f"{', '.join(contacts)}")
        
        # date and bill number
        today = nepali_datetime.date.today()
        today = today.strftime("%d/%m/%Y")
        canvas.drawString(doc.page_width - 2.6*self.rightMargin, doc.page_height - 1.3 * self.topMargin, f"Date        : {today}")
        # canvas.drawString(doc.page_width - 2.6*self.rightMargin, doc.page_height - 1.5 * self.topMargin, f"Page no   :  {canvas.getPageNumber()} of ")
        
        # customer details
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawCentredString(0.5 * (doc.page_width), doc.page_height - 2.1 * self.topMargin, "Ledger - Detailed")
        canvas.setFont("Helvetica", 12)

        #customer name 
        customer_name = self.ledger_details['customer']['full_name'] if self.ledger_details['customer']['full_name'] else self.ledger_details['customer']['company']
        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 2.5 * self.topMargin, f"A/C                :   {customer_name}")

        # report date
        from_ = self.ledger_details['from'] if self.ledger_details['from'] else self.ledger_details['account'][0]["date"]
        to = self.ledger_details['to'] if self.ledger_details['to'] else self.ledger_details['account'][-1]["date"]
        from_to_part = f"{from_} - {to}"

        canvas.drawString(self.leftMargin-0.2*inch, doc.page_height - 2.7 * self.topMargin, f"Report Date   :    {from_to_part}")
        
        # footer
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(0.5 * (doc.page_width), 1.3*self.bottomMargin, f"If you have any questions about this ledger, please contact.")
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(0.5 * (doc.page_width), 1.1*self.bottomMargin, f"Thank you for your business!")

        canvas.restoreState()


if __name__ == '__main__':
    company_info = {"company_name": "Satyam Hardware Pvt. Ltd. 2077-2078",
                    "phone_number": "9898989898",
                    "telephone": "071437282",
                    "pan_no": "1234",
                    "country": "Nepal",
                    "primary_owner": "Satyam Thapa",
                    "secondary_owner": "Subhyam Thapa",
                    "province": "Lumbini",
                    "district": "Rupandehi",
                    "municipality": "Butwal",
                    "ward": "11",
                    "toll": "Buddhanagar",
                    "zip_code": 44044}
    CURRENT_LEDGER_ACCOUNT = {
    'customer': {'id': 1, 'full_name': None, 'company': 'Nepal yatayat and vansar karyalaya', 'company_pan_no': '789465', 'phone_number': None, 'telephone': '545646', 'email': None, 'address': 'Kupandole, Lalitpur, in the middle of west'}, 
    'account': [{'id': 4, 'date': '03/04/2079', 'bill_id': 1, 'type': 'debit', 'description': 'Sales Bill #42342', 'amount': 22997, 'account_balance': '2,997.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit in SBL bank', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 1, 'date': '11/04/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 221000, 'account_balance': '3,997.00 Dr'}, 
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'},
                {'id': 3, 'date': '01/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Cash Deposit', 'amount': 221232, 'account_balance': '22,2,765.00 Dr'}, 
                {'id': 5, 'date': '03/08/2079', 'bill_id': None, 'type': 'debit', 'description': 'Cash Deposit', 'amount': 227894, 'account_balance': '22,10,659.00 Dr'}, 
                {'id': 6, 'date': '03/08/2079', 'bill_id': None, 'type': 'credit', 'description': 'Bank Deposit', 'amount': 298656, 'account_balance': '2,24,87,997.00 Cr'}], 
    'from': '', 
    'to': '', 
    'summary': {'dr_amount': 11891.0, 
                'cr_amount': 99888.0, 
                'account_balance': '87,997.00 Cr'}}

    name = CURRENT_LEDGER_ACCOUNT["customer"]["full_name"]
    company = CURRENT_LEDGER_ACCOUNT["customer"]["company"]
    
    from_ = CURRENT_LEDGER_ACCOUNT['from'] if CURRENT_LEDGER_ACCOUNT['from'] else CURRENT_LEDGER_ACCOUNT['account'][0]["date"]
    to = CURRENT_LEDGER_ACCOUNT['to'] if CURRENT_LEDGER_ACCOUNT['to'] else CURRENT_LEDGER_ACCOUNT['account'][-1]["date"]
    from_to_part = f"FROM_{from_}_To{to}"
    
    CustomerLedger('example.pdf',
                company_info=company_info, ledger_details=CURRENT_LEDGER_ACCOUNT, 
                title=f"{name if name else company}_{from_to_part}", author="IMAB System - Datakhoj",
                subject=f"A/C {name if name else company}_{from_to_part}")
