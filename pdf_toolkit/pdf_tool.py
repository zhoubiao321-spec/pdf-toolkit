#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, tkinter as tk, threading, io
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pypdf
from pypdf import PdfWriter, PdfReader
import pdfplumber
from reportlab.pdfgen import canvas

HAS_IMG2PDF = False
HAS_PDF2IMAGE = False
try:
    import img2pdf; HAS_IMG2PDF = True
except: pass
try:
    from pdf2image import convert_from_path; HAS_PDF2IMAGE = True
except: pass

class PDFToolkit:
    @staticmethod
    def merge_pdfs(pdf_list, output_path):
        writer = PdfWriter()
        for pdf in pdf_list:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)
        with open(output_path, "wb") as f: writer.write(f)
        return True

    @staticmethod
    def split_pdf(input_path, output_dir, mode="all"):
        reader = PdfReader(input_path)
        total = len(reader.pages)
        if mode == "all":
            for i in range(total):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])
                out = os.path.join(output_dir, f"page_{i+1}.pdf")
                with open(out, "wb") as f: writer.write(f)
            return total
        return 0

    @staticmethod
    def compress_pdf(input_path, output_path):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        for page in writer.pages:
            page.compress_content_streams()
        with open(output_path, "wb") as f: writer.write(f)
        return True

    @staticmethod
    def pdf_to_text(input_path, output_path):
        with pdfplumber.open(input_path) as pdf:
            text = ""
            for page in pdf.pages:
                t = page.extract_text()
                if t: text += t + "\n---\n"
        with open(output_path, "w", encoding="utf-8") as f: f.write(text)
        return True

    @staticmethod
    def pdf_to_excel(input_path, output_path):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        row_idx = 1; tables_count = 0
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    tables_count += 1
                    if tables_count > 1: row_idx += 2
                    for row in table:
                        for col, cell in enumerate(row, 1):
                            ws.cell(row=row_idx, column=col, value=str(cell) if cell else "")
                        row_idx += 1
        wb.save(output_path)
        return tables_count > 0

    @staticmethod
    def pdf_to_images(input_path, output_dir, fmt="png", dpi=200):
        if not HAS_PDF2IMAGE: raise ImportError("pdf2image not installed")
        images = convert_from_path(input_path, dpi=dpi)
        saved = []
        for i, img in enumerate(images):
            out = os.path.join(output_dir, f"page_{i+1}.{fmt}")
            img.save(out, fmt.upper())
            saved.append(out)
        return saved

    @staticmethod
    def images_to_pdf(image_list, output_path):
        from PIL import Image
        images = []
        for img_path in image_list:
            img = Image.open(img_path)
            if img.mode != "RGB": img = img.convert("RGB")
            images.append(img)
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            return True
        return False

    @staticmethod
    def add_watermark(input_path, output_path, text, opacity=0.3):
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for pn in range(len(reader.pages)):
            page = reader.pages[pn]
            w, h = float(page.mediabox.width), float(page.mediabox.height)
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=(w, h))
            c.setFillColor(0.5, 0.5, 0.5, opacity)
            c.setFont("Helvetica", 60)
            c.saveState()
            c.translate(w/2, h/2); c.rotate(45)
            c.drawCentredString(0, 0, text)
            c.restoreState(); c.save()
            packet.seek(0)
            page.merge_page(PdfReader(packet).pages[0])
            writer.add_page(page)
        with open(output_path, "wb") as f: writer.write(f)
        return True

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF \u529e\u516c\u5de5\u5177\u7bb1 v1.0")
        self.root.geometry("750x550")
        self.root.configure(bg="#f0f0f0")
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#2196F3", height=55)
        frame.pack(fill="x"); frame.pack_propagate(False)
        tk.Label(frame, text="PDF \u529e\u516c\u5de5\u5177\u7bb1",
            font=("Microsoft YaHei", 18, "bold"), bg="#2196F3", fg="white").pack(pady=10)

        bf = tk.Frame(self.root, bg="#f0f0f0")
        bf.pack(pady=12, padx=15, fill="x")
        btns = [
            ("\u5408\u5e76PDF",self.merge,"#4CAF50"), ("\u62c6\u5206PDF",self.split,"#FF9800"),
            ("\u538b\u7f29PDF",self.compress,"#9C27B0"), ("PDF\u8f6c\u6587\u5b57",self.to_text,"#2196F3"),
            ("PDF\u8f6cExcel",self.to_excel,"#00BCD4"), ("PDF\u8f6c\u56fe\u7247",self.to_images,"#E91E63"),
            ("\u56fe\u7247\u8f6cPDF",self.img2pdf,"#795548"), ("\u6dfb\u52a0\u6c34\u5370",self.watermark,"#607D8B"),
        ]
        for i,(t,cmd,c) in enumerate(btns):
            tk.Button(bf,text=t,command=cmd,font=("Microsoft YaHei",10),
                bg=c,fg="white",width=14,height=2,bd=0,cursor="hand2"
            ).grid(row=i//4,column=i%4,padx=5,pady=5,sticky="nsew")
        for i in range(4): bf.columnconfigure(i,weight=1)

        lf = tk.Frame(self.root, bg="#f0f0f0")
        lf.pack(fill="both",expand=True,padx=15,pady=(0,5))
        tk.Label(lf,text="\u5904\u7406\u65e5\u5fd7:",font=("Microsoft YaHei",9,"bold"),bg="#f0f0f0").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(lf,font=("Consolas",9),
            bg="#1e1e1e",fg="#d4d4d4",insertbackground="white",height=10)
        self.log.pack(fill="both",expand=True)

        sf = tk.Frame(self.root,bg="#333",height=28)
        sf.pack(fill="x",side="bottom"); sf.pack_propagate(False)
        self.status = tk.Label(sf,text="\u5c31\u7eea | \u552e\u4ef7: 15.8\u5143 | \u7ec8\u8eab\u4f7f\u7528",
            font=("Microsoft YaHei",9),bg="#333",fg="#ccc")
        self.status.pack(side="left",padx=10)

    def add_log(self,msg,level="info"):
        colors = {"info":"#d4d4d4","success":"#4CAF50","warn":"#FF9800","error":"#f44336"}
        c = colors.get(level,"#d4d4d4")
        self.log.insert("end",f"[{level.upper()}] {msg}\n")
        self.log.tag_config(level,foreground=c)
        self.log.see("end"); self.root.update()

    def run_task(self,fn,args=()):
        def wrapper():
            try:
                fn(*args)
                self.root.after(0,lambda:self.status.config(text="\u5b8c\u6210!"))
            except Exception as e:
                self.root.after(0,lambda:self.add_log(f"\u9519\u8bef: {e}","error"))
        threading.Thread(target=wrapper,daemon=True).start()

    def merge(self):
        files=filedialog.askopenfilenames(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not files: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58\u5408\u5e76",defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not out: return
        self.add_log(f"\u5408\u5e76 {len(files)} \u4e2a\u6587\u4ef6...")
        self.run_task(PDFToolkit.merge_pdfs,(list(files),out))
        self.add_log(f"\u5408\u5e76\u6210\u529f: {out}","success")

    def split(self):
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        d=filedialog.askdirectory(title="\u8f93\u51fa\u6587\u4ef6\u5939")
        if not d: return
        self.add_log("\u62c6\u5206\u4e2d...")
        self.run_task(self._do_split,(f,d))
    def _do_split(self,f,d):
        n=PDFToolkit.split_pdf(f,d,"all")
        self.add_log(f"\u62c6\u5206\u6210\u529f! {n}\u9875 -> {d}","success")

    def compress(self):
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58\u538b\u7f29\u540e",defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not out: return
        sb=os.path.getsize(f)
        self.add_log(f"\u538b\u7f29\u524d: {sb/1024:.1f}KB")
        def task():
            PDFToolkit.compress_pdf(f,out)
            sa=os.path.getsize(out)
            r=(1-sa/sb)*100
            self.add_log(f"\u538b\u7f29\u6210\u529f! {sb/1024:.1f}KB -> {sa/1024:.1f}KB (-{r:.1f}%)","success")
        self.run_task(task)

    def to_text(self):
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58\u6587\u672c",defaultextension=".txt",filetypes=[("TXT","*.txt")])
        if not out: return
        self.add_log("\u63d0\u53d6\u6587\u5b57\u4e2d...")
        self.run_task(PDFToolkit.pdf_to_text,(f,out))
        self.add_log(f"\u63d0\u53d6\u5b8c\u6210: {out}","success")

    def to_excel(self):
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58Excel",defaultextension=".xlsx",filetypes=[("Excel","*.xlsx")])
        if not out: return
        self.add_log("\u63d0\u53d6\u8868\u683c\u4e2d...")
        def task():
            ok=PDFToolkit.pdf_to_excel(f,out)
            self.add_log(f"\u8868\u683c\u63d0\u53d6\u6210\u529f: {out}","success") if ok else self.add_log("\u672a\u68c0\u6d4b\u5230\u8868\u683c","warn")
        self.run_task(task)

    def to_images(self):
        if not HAS_PDF2IMAGE: messagebox.showerror("\u9519\u8bef","\u7f3a\u5c11 pdf2image \u5e93"); return
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        d=filedialog.askdirectory(title="\u8f93\u51fa\u6587\u4ef6\u5939")
        if not d: return
        self.add_log("\u8f6c\u56fe\u7247\u4e2d...")
        self.run_task(PDFToolkit.pdf_to_images,(f,d))

    def img2pdf(self):
        files=filedialog.askopenfilenames(title="\u9009\u62e9\u56fe\u7247",filetypes=[("Image","*.png *.jpg *.jpeg *.bmp")])
        if not files: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58PDF",defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not out: return
        self.add_log(f"\u8f6c\u6362 {len(files)} \u5f20\u56fe\u7247...")
        self.run_task(PDFToolkit.images_to_pdf,(list(files),out))
        self.add_log(f"\u8f6c\u6362\u6210\u529f: {out}","success")

    def watermark(self):
        f=filedialog.askopenfilename(title="\u9009\u62e9PDF",filetypes=[("PDF","*.pdf")])
        if not f: return
        out=filedialog.asksaveasfilename(title="\u4fdd\u5b58\u6c34\u5370PDF",defaultextension=".pdf",filetypes=[("PDF","*.pdf")])
        if not out: return
        win=tk.Toplevel(self.root); win.title("\u6c34\u5370\u6587\u5b57"); win.geometry("300x120")
        win.resizable(False,False)
        tk.Label(win,text="\u8bf7\u8f93\u5165\u6c34\u5370\u6587\u5b57:").pack(pady=10)
        e=tk.Entry(win,font=("",12),width=25); e.insert(0,"\u673a\u5bc6\u6587\u4ef6"); e.pack()
        def ok():
            t=e.get(); win.destroy()
            self.add_log(f"\u6dfb\u52a0\u6c34\u5370: \\\"{t}\\\"")
            self.run_task(PDFToolkit.add_watermark,(f,out,t))
        tk.Button(win,text="\u786e\u8ba4",command=ok,bg="#2196F3",fg="white",width=10).pack(pady=8)
        win.transient(self.root); win.grab_set()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
