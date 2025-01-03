# PDF QA Full-Stack Application  
This is a full-stack application that allows users to upload PDF documents and ask questions about their content using Natural Language Processing (NLP).  

---
![image](https://github.com/user-attachments/assets/185adec9-68f1-477e-91f6-261f9a46ca2f)

## Features  
- **PDF Upload**: Users can upload PDF documents for processing.  
- **Question Answering**: Users can ask questions related to the uploaded PDF content, and the system provides answers using NLP.  
- **Real-Time Interaction**: The frontend provides a seamless experience for interacting with the system.  

## Architecture  
The application is divided into two main parts:  

1. **Backend**:  
   - **Framework**: FastAPI  
   - **Database**: SQLite/PostgreSQL  
   - **NLP Integration**: Utilizes LangChain, FAISS, and Gemini embeddings for document processing and question-answering.  
   - **File Handling**: Handles PDF file uploads and extracts text for NLP processing.  

2. **Frontend**:  
   - **Framework**: React.js  
   - **UI/UX**: Interactive interface for uploading files and querying documents.  




## Project Setup  

### Prerequisites  
Ensure you have the following installed:  
- **Python 3.8+**  
- **Node.js 14+**  
- **npm or Yarn**  
- **SQLite/PostgreSQL**  
- **FastAPI**  

### Backend Setup  

1. Clone the repository and navigate to the `backend` folder:  
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/backend
