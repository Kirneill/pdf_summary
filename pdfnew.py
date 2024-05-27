import os
import pdfplumber
from typing import List
import openai

# Initialize the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chat_completion(messages, model='gpt-3.5-turbo-0125'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content

def pdf_to_text(pdf_path: str) -> str:
    print(f"Extracting text from: {pdf_path}")
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Extracting text from page {page_num + 1}")
            text += page.extract_text() + "\n"
    return text

def split_text_into_chunks(text: str, chunk_size: int = 3000) -> List[str]:
    print("Splitting text into chunks")
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def summarize_text_gpt4(text: str, chunk_size: int = 3000) -> List[str]:
    text_chunks = split_text_into_chunks(text, chunk_size)
    summaries = []

    # Create or clear the chunks log file
    with open("chunks_log.txt", "w") as chunk_log_file:
        chunk_log_file.write("")

    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i + 1}/{len(text_chunks)}")
        with open("chunks_log.txt", "a") as chunk_log_file:
            chunk_log_file.write(f"Chunk {i+1}:\n{chunk}\n{'-'*40}\n")
        messages = [
            {"role": "system", "content": "You are a master class summarizer and note taker. Your task is to provide a concise, yet comprehensive summary that captures all crucial concepts and details. Ensure the summary is educational, highlights key points, and is structured in a way that facilitates easy learning and recall."},
            {"role": "user", "content": "Write a concise and comprehensive summary of the following text, ensuring to include all important details for a thorough understanding:\n\n" + chunk}
        ]
        summary = get_chat_completion(messages)
        summaries.append(summary)
        print(f"Chunk {i + 1} summarized")

    return summaries

def process_pdfs_in_directory(directory_path: str):
    print(f"Processing PDFs in directory: {directory_path}")
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            print(f"Processing file: {filename}")
            text = pdf_to_text(pdf_path)
            summaries = summarize_text_gpt4(text)

            summary_filename = filename.replace(".pdf", "_summary.txt")
            summary_path = os.path.join(directory_path, summary_filename)

            with open(summary_path, "w") as summary_file:
                for summary in summaries:
                    summary_file.write(summary + "\n\n")
            print(f"Summary for {filename} saved to {summary_filename}")

# Specify the directory containing PDF files
directory_path = r"H:/My Drive/PDF/IMPPDF"  # Use raw string to avoid invalid escape sequence
process_pdfs_in_directory(directory_path)
