from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, \
     NextPageTemplate, Paragraph, Table, TableStyle, Spacer

class CustomerBill(BaseDocTemplate):
    def __init__(self, filename, company_info, bill_details, 
                 show_discount=False, show_vat=False, show_tax=False, show_payment=False, **kwargs):
        super().__init__(filename, page_size=A4, _pageBreakQuick=0, **kwargs)
        self.company_info = company_info
        self.bill_details = bill_details

        self.page_width = (self.width + self.leftMargin * 2)
        self.page_height = (self.height + self.bottomMargin * 2)

        styles = getSampleStyleSheet()

        # Setting up the frames, frames are use for dynamic content not fixed page elements
        first_page_table_frame = Frame(self.leftMargin, 1.6*self.bottomMargin, self.width, self.height - 2.4 * inch, id='small_table')
        later_pages_table_frame = Frame(self.leftMargin, 1.6*self.bottomMargin, self.width, self.height - 2.4 * inch, id='large_table')

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

        tableMainStyle = TableStyle([
                                ("BOX",(0,0),(4,0),0.1,colors.black),
                                ("BOX",(0,0),(-1,-1),0.1,colors.black),
                                ("BACKGROUND",(0,0),(4,0),colors.grey),
                                ("TEXTCOLOR",(0,0),(4,0),colors.white),
                                ("FONT",(0,0),(4,0),"Helvetica-Bold",11),
                            ] + table_style)

        story.append(Table(data, repeatRows=1, colWidths=[0.5*inch, inch*3.1, 0.8*inch, 0.9*inch, inch],
                           style=tableMainStyle, splitByRow=1))
        
        final_data = []
        total_amount = self.bill_details["final"].get("total") if self.bill_details["final"].get("total") else 0
        if show_discount or show_vat or show_tax:
            subtotal = self.bill_details["final"].get("subtotal") if self.bill_details["final"].get("subtotal") else 0
            final_data.append(["Subtotal", "{:,.2f}".format(float(subtotal))])
            if show_discount:
                discount = self.bill_details["final"].get("discount") if self.bill_details["final"].get("discount") else 0
                final_data.append(["Discount", "{:,.2f}".format(float(discount))])
            if show_vat:
                vat = self.bill_details["final"].get("vat") if self.bill_details["final"].get("vat") else 0
                final_data.append(["Vat", "{:,.2f}".format(float(vat))])
            if show_tax:
                tax = self.bill_details["final"].get("tax") if self.bill_details["final"].get("tax") else 0
                final_data.append(["Tax", "{:,.2f}".format(float(tax))])

        
        totalStyle = ParagraphStyle("totalStyle", fontName="Helvetica-Bold", fontSize=11)
        final_data += [[Paragraph("TOTAL", totalStyle), "{:,.2f}".format(float(total_amount))]]
        
        if show_payment:
            paid_amount = self.bill_details["final"].get("paid_amount") if self.bill_details["final"].get("paid_amount") else 0
            final_data.append([Paragraph("PAID", totalStyle), "{:,.2f}".format(float(paid_amount))])
            final_data.append([Paragraph("DUE", totalStyle), "{:,.2f}".format(float(total_amount)-float(paid_amount))])
        
        table_sub_style = []
        if show_discount or show_vat or show_tax:
            table_sub_style.append(("LINEABOVE", (0,-1), (1,-1), 2, colors.black))
        tableSubStyle = TableStyle([
                                ("FONT",(0,0),(-1,-1),"Helvetica",11),
                                ("NOSPLIT",(0,0),(-1,-1))] + table_sub_style)
        
        story.append(Spacer(20, 20))
        story.append(Paragraph("NOTE: All prices are in Nepali Rupees(Rs)."))
        story.append(Table(final_data, repeatRows=1, colWidths=[0.8*inch, inch], 
            style=tableSubStyle, hAlign="RIGHT"))
        
        self.build(story)


    def get_data_for_table(self):
        headings = ["S No.", "Particulars","Quantity", "Rate", "Amount"]
        rows = []
        for index, details in enumerate(self.bill_details.get("products").values()):
            rows.append([str(index+1), str(details["product_name"]), str(details["quantity"]), "{:,.2f}".format(float(details["rate"])), "{:,.2f}".format(float(details["rate"])*float(details["quantity"]))])
        
        return [headings] + rows


    def on_first_page(self, canvas, doc):
        canvas.saveState()
        # Add the logo and other default stuff
        self.add_default_info(canvas, doc)
        canvas.restoreState()

    def add_default_info(self, canvas, doc):
        canvas.saveState()
        # company name
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(self.leftMargin, doc.page_height - 1 * self.topMargin, f"{self.company_info.get('company_name')}")
        # additinonal info
        canvas.setFont("Helvetica", 12)
        canvas.drawString(self.leftMargin, doc.page_height - 1.3 * self.topMargin, f"PAN no: {self.company_info.get('pan_no')}")
        canvas.drawString(self.leftMargin, doc.page_height - 1.5 * self.topMargin, f"{self.company_info.get('municipality')} {self.company_info.get('ward')}, {self.company_info.get('district')}, {self.company_info.get('province')}, {self.company_info.get('country')}")

        phone_num = self.company_info.get('phone_number')
        telephone = self.company_info.get('telephone')
        contacts = []
        if phone_num: contacts.append(phone_num) 
        if telephone: contacts.append(telephone) 
        
        canvas.drawString(self.leftMargin, doc.page_height - 1.7 * self.topMargin, f"{', '.join(contacts)}")
        # date and bill number
        bill_number = self.bill_details['final'].get('bill_number')
        if not bill_number:
            raise Exception("Missing bill number.")
        date_of_bill = self.bill_details['final'].get('date') if self.bill_details['final'].get('date') else "--------"
        canvas.drawString(doc.page_width - 2.6*self.rightMargin, doc.page_height - 1.3 * self.topMargin, f"Date       : {date_of_bill}")
        canvas.drawString(doc.page_width - 2.6*self.rightMargin, doc.page_height - 1.5 * self.topMargin, f"Bill no     : {bill_number}")
        
        # customer details
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(doc.leftMargin, doc.height - 0.2*inch, "BILL TO")
        canvas.setFont("Helvetica", 12)

        customer_phone_num = self.bill_details['customer']['phone_number']
        customer_telephone = self.bill_details['customer']['telephone']
        customer_contacts = []
        if customer_phone_num: customer_contacts.append(customer_phone_num) 
        if customer_telephone: customer_contacts.append(customer_telephone)
        if not (customer_phone_num or customer_telephone): customer_contacts.append("---------")

        canvas.drawString(self.leftMargin, doc.height - 0.4 * inch, 
                        f"Customer Name :   {self.bill_details['customer']['full_name']}                     Contact:    {', '.join(customer_contacts)}")
        customer_company = self.bill_details['customer'].get('company') if self.bill_details['customer'].get('company') else "--------"
        canvas.drawString(self.leftMargin, doc.height - 0.6 * inch, 
                        f"Company            :   {customer_company}")
        
        # footer
        canvas.setFont("Helvetica", 9)
        canvas.drawCentredString(0.5 * (doc.page_width), 1.5*self.bottomMargin, f"If you have any questions about this bill, please contact.")
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(0.5 * (doc.page_width), 1.3*self.bottomMargin, f"Thank you for your business!")
        
        # page number
        # page_number = str(doc.getPageNumber())

        canvas.restoreState()


if __name__ == '__main__':
    company_info = {"company_name": "Satyam Hardware Pvt Ltd",
                    "phone_number": "9898989898",
                    "phone_number": "telephone",
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
    bill_details = {
    "customer":{"full_name":"Suryam Thapa", "phone_number":"", "company":"", "telephone":""},
    "products":{
        11:{"product_name":"what the hell is this","quantity":124, "rate":456},
        13:{"product_name":"what the hell is this","quantity":124, "rate":456459},
        14:{"product_name":"what the hell is this","quantity":124, "rate":456},
        15:{"product_name":"what the hell is this","quantity":124, "rate":456},
        16:{"product_name":"what the helasdfasdfasdfasdfasdfl is this","quantity":124, "rate":456},
        17:{"product_name":"what the hell is this","quantity":124, "rate":456},
        18:{"product_name":"what the hell is this","quantity":124, "rate":456},
        19:{"product_name":"what the hell is this","quantity":124, "rate":456},
        20:{"product_name":"what the hell is this","quantity":124, "rate":456},
        21:{"product_name":"what the hell is this","quantity":124, "rate":456},
        22:{"product_name":"what the hell is this","quantity":124, "rate":456},
        23:{"product_name":"what the hell is this","quantity":124, "rate":456},
        24:{"product_name":"what the helasdfasdfasdfasdfasdfl is this","quantity":124, "rate":456},
        25:{"product_name":"what the hell is this","quantity":124, "rate":456},
        26:{"product_name":"what the hell is this","quantity":124, "rate":456},
        27:{"product_name":"what the hell is this","quantity":124, "rate":456},
        28:{"product_name":"what the hell is this","quantity":124, "rate":456},
        29:{"product_name":"what the hell is this","quantity":124, "rate":456},
        31:{"product_name":"what the hell is this","quantity":124, "rate":456},
        41:{"product_name":"what the hell is this","quantity":124, "rate":456},
        32:{"product_name":"what the helasdfasdfasdfasdfasdfl is this","quantity":124, "rate":456},
        42:{"product_name":"what the hell is this","quantity":124, "rate":456},
        33:{"product_name":"what the hell is this","quantity":124, "rate":456},
        43:{"product_name":"what the hell is this","quantity":124, "rate":456},
        34:{"product_name":"what the helasdfasdfasdfasdfasdfl is this","quantity":124, "rate":456},
        44:{"product_name":"what the hell is this","quantity":124, "rate":456},
        35:{"product_name":"what the hell is this","quantity":124, "rate":456},
        45:{"product_name":"what the hell is this","quantity":124, "rate":456},
        51:{"product_name":"what the hell is this","quantity":124, "rate":456},
        52:{"product_name":"what the hell is this","quantity":124, "rate":456},
        53:{"product_name":"what the hell is this","quantity":124, "rate":456},
        54:{"product_name":"what the hell is this","quantity":124, "rate":456}
    },
    "extra":{"discount": "34", "vat":"454"},
    "final":{
        "date": "2020/11/12",
        "bill_number":"1234",
        "subtotal":"12444.00",
        "discount":"2355.00",
        "vat":"345664354.00",
        "total":"556667.00",
        "paid_amount":""
    }
}
    CustomerBill('example.pdf', 
                company_info=company_info, bill_details=bill_details, 
                title=f"{bill_details['customer']['full_name']} 2020/11/12", author="IMAB System - Datakhoj",
                subject=f"Bill To {bill_details['customer']['full_name']}", show_discount=False, show_vat=False, show_tax=False, show_payment=False)