from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from time import sleep
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    open_order_website()
    loop_orderlist(get_orders_csv())
    archive_receipts()


def open_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    

def get_orders_csv():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    return(library.read_table_from_csv("orders.csv"))

def loop_orderlist(orders):
    for item in orders:
        print(item["Order number"])
        fill_order_form(item)

def fill_order_form(orderitem):
    page = browser.page()
    page.click("#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")
    page.select_option("#head", orderitem["Head"])
    page.check("#id-body-" + orderitem["Body"])
    page.fill("#root > div > div.container > div > div.col-sm-7 > form > div:nth-child(3) > input", orderitem['Legs'])
    page.fill("#address", orderitem["Address"])
    page.click("#preview")
    while True:
        page.click("#order")
        if page.is_visible("#root > div > div.container > div > div.col-sm-7 > div.alert"):
            print("Error, resubmitting")
        else:
            break
    pdfpath = store_receipt_as_pdf(orderitem["Order number"])
    scpath = take_receipt_screenshot(orderitem["Order number"])
    embed_sc_into_pdf(scpath, pdfpath)
    page.click("#order-another")

def store_receipt_as_pdf(orderno):
    pdf = PDF()
    page = browser.page()
    receipt_html = page.inner_html("#receipt")
    pdf.html_to_pdf(receipt_html, "output/receipts/receipt"+orderno + ".pdf")
    return("output/receipts/receipt"+orderno + ".pdf")


def take_receipt_screenshot(orderno):
    page = browser.page()
    page.locator("#receipt").screenshot(path="output/receipts/receipt"+orderno + ".png")
    return("output/receipts/receipt"+orderno + ".png")

def embed_sc_into_pdf(scpath, pdfpath):
    pdf = PDF()
    
    pdf.add_files_to_pdf(
        files = [scpath],
        target_document= pdfpath,
        append = True
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip(
        "./output/receipts",
        "./output/receipts.zip",
        include="*.pdf",
    )

    



