import os
import pdfplumber
from openai import OpenAI

def pdf_to_text(file_path):
    """
    Extracts text from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    text = ''
    print(f"Opening PDF file: {file_path}")
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + '\n'
    print("Finished extracting text from PDF")
    return text

def summarize_text_gpt4(text, max_chunk_size=3000):
    """
    Summarizes the given text using the GPT-4 model.

    Args:
        text (str): The text to be summarized.
        max_chunk_size (int): The maximum number of tokens to process at a time.

    Returns:
        list: A list of summaries for each text chunk.
    """
    summaries = []
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    print("Starting text summarization with GPT-4")
    total_chunks = (len(text) + max_chunk_size - 1) // max_chunk_size  # Calculate total number of chunks
    for i in range(0, len(text), max_chunk_size):
        chunk_number = i // max_chunk_size + 1
        chunk = text[i:i+max_chunk_size]
        print(f"\nSummarizing chunk {chunk_number}/{total_chunks}:\n{chunk[:60]}...")  # Print the progress
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a master class summarizer and note taker."},
                {"role": "user", "content": "Write a concise summary of the following text:\n\n" + chunk}
            ],
            model="gpt-3.5-turbo-0125",
            temperature=0.5,
            max_tokens=1500,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print(f"Response received: {response}")

        message_content = response.choices[0].message.content.strip()
        summaries.append(message_content)
        print(f"Chunk summary {chunk_number}/{total_chunks}:\n{message_content}\n{'-'*40}")
    print("Finished summarizing text")
    return summaries

# Example usage
pdf_folder_path = 'H:/My Drive/PDF/IMPPDF/'

# List all PDF files in the folder
pdf_files = [f for f in os.listdir(pdf_folder_path) if f.endswith('.pdf')]

# Process each PDF file
for pdf_file in pdf_files:
    pdf_file_path = os.path.join(pdf_folder_path, pdf_file)
    print(f"Reading PDF file from: {pdf_file_path}")
    full_text = pdf_to_text(pdf_file_path)
    print("PDF text extraction complete. Starting summarization.")
    
    summaries = summarize_text_gpt4(full_text)
    
    # Output the summaries
    print("Summaries:")
    
    # Extract the base name and create the output file path
    base_name = os.path.splitext(pdf_file)[0]
    output_file_path = os.path.join(pdf_folder_path, f'{base_name}_summary.txt')
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for idx, summary in enumerate(summaries, start=1):
            f.write(f"Summary {idx}:\n{summary}\n\n")
    
    print(f"Summaries saved to {output_file_path}")
