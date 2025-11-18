import os
from classifier import classify_file

folder = "./dummy_documents"
for file in os.listdir(folder):
    if file.endswith(('.pdf', '.png', '.jpg', '.docx')):
        result = classify_file(os.path.join(folder, file))
        print(f"\n{'='*60}")
        print(f"FILE: {file}")
        print(f"{'='*60}")
        print(f"Document Type: {result['document_type']}")
        print(f"Confidence: {result['confidence']}")
        
        # Display extracted entities
        if result['entities']:
            print(f"\nExtracted Entities:")
            for entity_name, entity_data in result['entities'].items():
                confidence = entity_data['confidence']
                value = entity_data['value']
                print(f"  {entity_name}: {value} (Confidence: {confidence:.2f})")
        else:
            print("\nNo entities extracted.")