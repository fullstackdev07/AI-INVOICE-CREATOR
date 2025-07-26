# AI-Powered Invoice Creator

This project is a smart tool that helps users create, edit, and export professional invoice templates using the power of AI.

## How to Run This Project

You need to run the **Backend** and the **Frontend** servers simultaneously in two separate terminal windows.

---

### 1. Backend Setup (FastAPI)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    *   **Mac/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browser binaries:**
    ```bash
    playwright install
    ```

5.  **Set up your environment variables:**
    *   Copy the example file: `cp .env.example .env` (or `copy .env.example .env` on Windows).
    *   Open the newly created `.env` file and **add your OpenAI API key**.

6.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend will now be running at `http://127.0.0.1:8000`. Keep this terminal open.

---

### 2. Frontend Setup (React)

1.  **Open a new terminal window.**

2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

3.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

4.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend will now be running at `http://localhost:5173`.

---

### 3. Usage

1.  Open your web browser and go to **`http://localhost:5173`**.
2.  Type a description of the invoice you want in the input box.
3.  Click "Generate".
4.  The AI will create a template, which will appear in the editor below.
5.  You can make changes in the editor.
6.  Click one of the "Export" buttons to download your invoice in the desired format.