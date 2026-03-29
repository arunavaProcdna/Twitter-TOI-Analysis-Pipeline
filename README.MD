
---

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/arunavaProcdna/Twitter-TOI-Analysis-Pipeline/
cd Twitter-TOI-Analysis-Pipeline
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

**On macOS / Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Project

```bash
python3 main.py
```

---

##  Project Structure

```
.
├── analysis/
├── final_output/
├── input/
├── test/
├── llm_call.py
├── main.py
├── thread_wise_processor_first.py
├── thread_wise_processor_second.py
├── utils_graph.py
├── utility.py
├── requirements.txt
├── README.md
├── .gitignore        
```

input/ → Raw tweet data (.xlsx files)
analysis/ → Intermediate processing
final_output/ → Final TOI outputs (JSON/XLSX)
test/ → Test scripts and validation
.xlsx files are ignored in Git but used locally
Add your API keys in a .env file if required
