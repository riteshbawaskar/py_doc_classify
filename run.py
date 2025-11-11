import os
from classifier import classify_file

folder = "./dummy_documents"
for file in os.listdir(folder):
    if file.endswith(('.pdf', '.png', '.jpg', '.docx')):
        result = classify_file(os.path.join(folder, file))
        print(f"{file}: {result['document_type']}")