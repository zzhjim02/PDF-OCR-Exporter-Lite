# PDF OCR Text Extraction Tool / PDF OCR文本提取工具

A GUI tool for extracting OCR results from PDF files and saving them as TXT files.
一个图形化界面的工具，用于从PDF文件中提取OCR识别结果并保存为TXT文件。

## Features / 功能特点

-   **Graphical Interface Operation / 图形化界面操作**: Simple and easy to use. / 简单易用。

-   **Batch Processing / 批量处理**: Supports processing large numbers of PDF files. / 支持批量处理大量PDF文件。

-   **Preserves Folder Structure / 保留文件夹结构**: Maintains the original directory structure of the source files. / 保留原有的文件夹结构。

-   **Supports Double-layer PDFs / 支持双层PDF**: Can extract text from PDFs containing an OCR text layer. / 支持双层PDF（包含OCR文本层）。

-   **Multiple Extraction Methods / 多种提取方法**: Offers a choice of extraction methods. / 多种提取方法可选。

-   **Real-time Progress Display / 实时进度显示**: Shows processing progress and logs in real time. / 实时显示处理进度和日志。

## Installation Dependencies / 安装依赖

### Required Dependencies / 必需依赖

```bash
pip install pymupdf 
pip install pdfplumber
```

## Usage Instructions / 使用方法

### Launch the Program / 启动程序

```bash
python pdf_ocr_extractor.py
```

### Operation Steps / 操作步骤
1.	Click the “**Select Folder**” button to choose the source folder containing PDF files. / 点击“**选择文件夹**”按钮，选择包含PDF文件的源文件夹。

2.	Click the “**Select Folder**” button to choose the output folder for TXT files. / 点击“**选择文件夹**”按钮，选择TXT文件的输出文件夹。

3.	**Select an extraction method**: / **选择提取方法**：
```bash
 
  Auto Select / 自动选择: The program automatically selects an available extraction library. / 程序自动选择可用的提取库。     
	
  PyMuPDF: Uses the PyMuPDF library for extraction (recommended). / 使用PyMuPDF库提取（推荐）。
	
  pdfplumber: Uses the pdfplumber library for extraction. / 使用pdfplumber库提取。
```
	
4.	Click the “**Start Extraction**” button to begin processing. / 点击”**开始提取**”按钮开始处理。

5.	After processing is complete, view the extracted TXT files in the output folder. / 处理完成后，可在输出文件夹查看提取的TXT文件。

## Notes / 注意事项
-   The program will **recursively scan all** PDF files in the source folder. / 程序会**递归扫描**源文件夹中的**所有**PDF文件。

-   The output TXT files will maintain the **same folder structure** as the PDF files. / 输出的TXT文件会保持与PDF文件**相同的文件夹结构**。

-   If the PDF file **does not have an OCR text layer**, the extraction result **may be empty**. / 如果PDF文件**没有OCR文本层**，提取结果**可能为空**。

-   For scanned PDFs (images), OCR recognition must be performed **first to extract text**. / 对于扫描版PDF（图片），需要**先进行OCR识别**才能提取文本。

## About Double-layer PDFs / 关于双层PDF

A double-layer PDF is a PDF file that contains two layers of content: / 双层PDF是指包含两层内容的PDF文件：

-   **Image Layer / 图像层**: The original scanned image. / 原始扫描图像。

-   **Text Layer / 文本层**: The OCR recognition results (transparent text). / OCR识别结果（透明文本）。

This tool is specifically designed to extract the OCR text layer content from double-layer PDFs./ 本工具专门用于提取双层PDF中的OCR文本层内容。

## System Requirements / 系统要求

```bash

Python 3.6 or higher / Python 3.6 或更高版本

Windows / macOS / Linux
```

## License / 许可证
```bash
MIT License
```
