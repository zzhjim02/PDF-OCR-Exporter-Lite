#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR文本提取工具
从PDF文件中提取OCR识别结果并保存为TXT文件
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import queue
import multiprocessing
from multiprocessing import Pool, cpu_count, Manager

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def process_single_pdf(pdf_path, output_path, method):
    """处理单个PDF文件（用于多进程）"""
    try:
        # 创建输出目录
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 提取文本
        text = extract_text_from_pdf_static(pdf_path, method)
        
        if text.strip():
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return ("success", "")
        else:
            return ("empty", "")
    
    except Exception as e:
        return ("error", str(e))


def extract_text_from_pdf_static(pdf_path, method="auto"):
    """从PDF提取文本（静态方法，用于多进程）"""
    text_parts = []
    
    # 确定使用的方法
    use_pymupdf = False
    use_pdfplumber = False
    
    if method == "pymupdf":
        use_pymupdf = fitz is not None
    elif method == "pdfplumber":
        use_pdfplumber = pdfplumber is not None
    else:  # auto
        use_pymupdf = fitz is not None
        if not use_pymupdf:
            use_pdfplumber = pdfplumber is not None
    
    # 使用PyMuPDF提取
    if use_pymupdf:
        try:
            doc = fitz.open(str(pdf_path))
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 提取文本块（保留格式）
                blocks = page.get_text("blocks")
                page_text = []
                
                for block in blocks:
                    if block[6] == 0:  # 文本块
                        page_text.append(block[4])
                
                if page_text:
                    text_parts.append(f"--- 第 {page_num + 1} 页 ---\n")
                    text_parts.append("\n".join(page_text))
                    text_parts.append("\n\n")
            
            doc.close()
            
            if text_parts:
                return "".join(text_parts)
        
        except Exception as e:
            if method == "pymupdf":
                raise e
    
    # 使用pdfplumber提取
    if use_pdfplumber:
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- 第 {page_num + 1} 页 ---\n")
                        text_parts.append(text)
                        text_parts.append("\n\n")
            
            if text_parts:
                return "".join(text_parts)
        
        except Exception as e:
            if method == "pdfplumber":
                raise e
    
    # 如果都失败，返回空字符串
    return "".join(text_parts) if text_parts else ""


class PDFExtractorApp:
    """PDF OCR文本提取应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF OCR文本提取工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 处理状态
        self.is_processing = False
        self.stop_flag = False
        self.message_queue = queue.Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动消息处理
        self.process_messages()
        
        # 检查依赖
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查必要的依赖库"""
        if fitz is None and pdfplumber is None:
            messagebox.showwarning(
                "依赖警告",
                "未检测到PDF处理库。\n\n"
                "请安装以下库之一：\n"
                "pip install pymupdf\n"
                "或\n"
                "pip install pdfplumber\n\n"
                "推荐使用 pymupdf，提取效果更好。"
            )
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 源文件夹选择
        source_frame = ttk.LabelFrame(main_frame, text="源文件夹", padding="5")
        source_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.source_path = tk.StringVar()
        ttk.Entry(source_frame, textvariable=self.source_path, 
                  state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(source_frame, text="选择文件夹", 
                   command=self.select_source_folder).pack(side=tk.RIGHT)
        
        # 输出文件夹选择
        output_frame = ttk.LabelFrame(main_frame, text="输出文件夹", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.output_path = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path,
                  state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="选择文件夹",
                   command=self.select_output_folder).pack(side=tk.RIGHT)
        
        # 选项设置
        options_frame = ttk.LabelFrame(main_frame, text="选项设置", padding="5")
        options_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 提取方法选择
        method_frame = ttk.Frame(options_frame)
        method_frame.pack(fill=tk.X, pady=(0, 3))
        
        ttk.Label(method_frame, text="提取方法:").pack(side=tk.LEFT, padx=(0, 5))
        self.extract_method = tk.StringVar(value="auto")
        
        methods = [("自动选择", "auto"), ("PyMuPDF", "pymupdf"), ("pdfplumber", "pdfplumber")]
        for text, value in methods:
            ttk.Radiobutton(method_frame, text=text, value=value,
                           variable=self.extract_method).pack(side=tk.LEFT, padx=5)
        
        # 进程数设置
        process_frame = ttk.Frame(options_frame)
        process_frame.pack(fill=tk.X)
        
        ttk.Label(process_frame, text="并行进程数:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.process_count = tk.StringVar(value=str(cpu_count()))
        self.process_spinbox = ttk.Spinbox(process_frame, from_=1, to=cpu_count() * 2,
                                           textvariable=self.process_count, width=5)
        self.process_spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(process_frame, text=f"(推荐: {cpu_count()} 个CPU核心)").pack(side=tk.LEFT)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="处理进度", padding="5")
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 3))
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack(fill=tk.X)
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state='disabled', height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, 
                                  command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.start_button = ttk.Button(button_frame, text="开始提取", 
                                       command=self.start_extraction, width=12)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", 
                                      command=self.stop_extraction, state='disabled', width=8)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="清空日志", 
                   command=self.clear_log, width=10).pack(side=tk.LEFT, padx=(0, 5))
        
        # 统计信息
        self.stats_label = ttk.Label(button_frame, text="")
        self.stats_label.pack(side=tk.RIGHT)
    
    def select_source_folder(self):
        """选择源文件夹"""
        folder = filedialog.askdirectory(title="选择包含PDF文件的源文件夹")
        if folder:
            self.source_path.set(folder)
    
    def select_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory(title="选择TXT文件输出文件夹")
        if folder:
            self.output_path.set(folder)
    
    def log_message(self, message, level="INFO"):
        """添加日志消息"""
        self.message_queue.put(("log", message, level))
    
    def update_status(self, message):
        """更新状态"""
        self.message_queue.put(("status", message))
    
    def update_progress(self, value):
        """更新进度"""
        self.message_queue.put(("progress", value))
    
    def update_stats(self, processed, total, success, failed):
        """更新统计信息"""
        self.message_queue.put(("stats", processed, total, success, failed))
    
    def process_messages(self):
        """处理消息队列"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
                if msg[0] == "log":
                    _, message, level = msg
                    self._add_log(message, level)
                elif msg[0] == "status":
                    self.status_label.config(text=msg[1])
                elif msg[0] == "progress":
                    self.progress_var.set(msg[1])
                elif msg[0] == "stats":
                    _, processed, total, success, failed = msg
                    self.stats_label.config(
                        text=f"已处理: {processed}/{total} | 成功: {success} | 失败: {failed}"
                    )
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_messages)
    
    def _add_log(self, message, level="INFO"):
        """添加日志到文本框"""
        self.log_text.config(state='normal')
        prefix = f"[{level}] "
        self.log_text.insert(tk.END, prefix + message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def start_extraction(self):
        """开始提取"""
        source = self.source_path.get()
        output = self.output_path.get()
        
        if not source:
            messagebox.showerror("错误", "请选择源文件夹")
            return
        
        if not output:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        if not os.path.isdir(source):
            messagebox.showerror("错误", "源文件夹不存在")
            return
        
        if fitz is None and pdfplumber is None:
            messagebox.showerror("错误", "未安装PDF处理库，无法提取")
            return
        
        # 禁用按钮
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_processing = True
        self.stop_flag = False
        
        # 启动处理线程
        thread = threading.Thread(target=self.extract_pdfs, 
                                  args=(source, output), daemon=True)
        thread.start()
    
    def stop_extraction(self):
        """停止提取"""
        self.stop_flag = True
        self.update_status("正在停止...")
    
    def extract_pdfs(self, source_dir, output_dir):
        """提取PDF文件"""
        try:
            # 查找所有PDF文件
            source_path = Path(source_dir)
            pdf_files = list(source_path.rglob("*.pdf"))
            
            if not pdf_files:
                self.log_message("未找到PDF文件", "WARNING")
                self.finish_extraction()
                return
            
            total = len(pdf_files)
            self.log_message(f"找到 {total} 个PDF文件")
            
            # 获取提取方法和进程数
            method = self.extract_method.get()
            try:
                num_processes = int(self.process_count.get())
                num_processes = max(1, min(num_processes, cpu_count() * 2))
            except:
                num_processes = cpu_count()
            
            self.log_message(f"使用 {num_processes} 个并行进程")
            
            # 准备任务列表
            tasks = []
            for pdf_file in pdf_files:
                rel_path = pdf_file.relative_to(source_path)
                output_file = Path(output_dir) / rel_path.with_suffix('.txt')
                tasks.append((str(pdf_file), str(output_file), method))
            
            # 处理统计
            processed = 0
            success = 0
            failed = 0
            
            # 使用进程池并行处理
            with Pool(processes=num_processes) as pool:
                results = []
                for i, task in enumerate(tasks):
                    if self.stop_flag:
                        self.log_message("用户取消操作", "WARNING")
                        pool.terminate()
                        break
                    
                    # 异步提交任务
                    result = pool.apply_async(process_single_pdf, task)
                    results.append((result, task[0], task[1]))
                
                # 收集结果
                for i, (result, pdf_path, output_path) in enumerate(results):
                    if self.stop_flag:
                        break
                    
                    try:
                        status, message = result.get(timeout=300)
                        rel_path = Path(pdf_path).relative_to(source_path)
                        
                        if status == "success":
                            self.log_message(f"成功: {rel_path}")
                            success += 1
                        elif status == "empty":
                            self.log_message(f"无文本内容: {rel_path}", "WARNING")
                            failed += 1
                        else:
                            self.log_message(f"失败: {rel_path} - {message}", "ERROR")
                            failed += 1
                        
                    except Exception as e:
                        rel_path = Path(pdf_path).relative_to(source_path)
                        self.log_message(f"失败: {rel_path} - {str(e)}", "ERROR")
                        failed += 1
                    
                    processed += 1
                    progress = (processed / total) * 100
                    self.update_progress(progress)
                    self.update_stats(processed, total, success, failed)
            
            # 完成
            self.log_message(f"\n处理完成！成功: {success}, 失败: {failed}")
            
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}", "ERROR")
        
        finally:
            self.finish_extraction()
    
    def extract_text_from_pdf(self, pdf_path, method="auto"):
        """从PDF提取文本"""
        return extract_text_from_pdf_static(pdf_path, method)
    
    def finish_extraction(self):
        """完成提取"""
        self.is_processing = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.update_status("就绪")


def main():
    """主函数"""
    # Windows多进程保护：确保子进程不会重新创建GUI
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = PDFExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
