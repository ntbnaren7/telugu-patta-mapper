# 🗺️ Telugu Patta Mapper

The **Telugu Patta Mapper** is a project developed to map and visualize **land records (patta) in Telugu**. It helps in digitizing and linking patta documents to geographic locations, making it easier to analyze and manage land ownership information.

This project was developed as a part of **SIH 2025** to facilitate automated land record mapping and visualization.

---

## 🚀 Features

- **Patta Document Parsing**  
  Extracts relevant details from Telugu patta documents, such as owner name, survey number, land type, and area.

- **Geospatial Mapping**  
  Maps extracted patta information to geographic coordinates for visualization.

- **Structured Data Output**  
  Outputs cleaned and structured data in formats like CSV or JSON, ready for analytics or GIS applications.

- **Batch Processing**  
  Supports processing multiple patta documents at once for large-scale mapping.

---

## 🛠️ Installation

Clone the repository:
```bash
git clone https://github.com/your-username/telugu-patta-mapper.git
cd telugu-patta-mapper
```

Install dependencies (Python example):
```python
pip install -r requirements.txt
```
Ensure that necessary OCR tools and geospatial libraries (like pytesseract, geopandas) are installed.

---

## ⚡ Usage

Extract and map a single patta document:
```python
from patta_mapper import extract_and_map

document_path = "documents/sample_patta.pdf"
mapped_data = extract_and_map(document_path)

print(mapped_data)
```

Process multiple patta documents:
```python
from patta_mapper import batch_process

documents = ["documents/patta1.pdf", "documents/patta2.pdf"]
results = batch_process(documents)

for res in results:
    print(res)
```

---

## 📚 How It Works

### OCR Extraction
Reads Telugu patta documents using OCR to extract text.

### Field Parsing
Identifies key entities like owner name, survey number, area, and land type.

### Geospatial Mapping
Links the extracted land records to coordinates for mapping and visualization.

### Structured Output
Returns data in JSON or CSV format for analytics or GIS applications.

---

## 🎯 Use Cases

- Digitizing and managing **land records** efficiently.  
- Visualizing **land ownership and distribution** on maps.  
- Facilitating government or administrative processes for **land management**.  
- Supporting research and analytics on **land ownership patterns**.

---

## 👥 Contributing

Contributions are welcome!  

1. Fork the repo  
2. Create a branch for your feature/fix  
3. Submit a pull request  

---

## 📄 License

MIT License

---

## 🔗 References

- Telugu patta documents available from government portals.  
- OCR and geospatial libraries for document parsing and mapping.
