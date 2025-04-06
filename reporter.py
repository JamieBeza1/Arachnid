from docx import Document
from datetime import datetime


class Reporter:
    def __init__(self, articles):
        #self.title = title
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.master_title = f"{self.date} - News Report"
        self.articles = articles
        
    def generate_report(self):
        document = Document()
        
        for title, content in self.articles.items():
            document.add_heading(title, level=1)
            
            if "Summary" in content:
                document.add_paragraph(content["Summary"])
            else:
                document.add_paragraph("No summary available for this article.")                
        
        filename = f"{self.master_title}.docx"
        document.save(filename)
        print(f"Report saved as \033[1,32m{filename}\033[0m")
        