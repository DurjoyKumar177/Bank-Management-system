# Amar Bank - Django-Based Bank Management System

Amar Bank is a secure and efficient **Django-based Bank Management System** that provides users with seamless banking operations, including deposits, withdrawals, transfers, loan requests, and transaction history. It features **email authentication, admin-approved loans, and a user-friendly interface** to ensure smooth banking experiences.

## 🚀 Features
- 🔐 **User Authentication** (Signup, Login, Logout, Password Reset via Email)
- 💰 **Deposit & Withdrawal** System
- 🔄 **Fund Transfers** between accounts
- 🏦 **Loan Requests & Approval** (Admin-Managed)
- 📜 **Transaction History** with Filtering
- 👤 **Profile Management**
- ✉️ **Email Notifications** for Key Banking Activities
- 🎨 **Responsive UI** with Bootstrap 5 & Crispy Forms

## 🛠️ Technologies Used
- **Backend:** Django, Python
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, Bootstrap 5
- **Forms:** Django Crispy Forms
- **Email Services:** Django Email Authentication & Notification System
- **Deployment:** Hosted on Render

## 🎬 Live Demo
🔗 [Check it out on Render](#) *(https://bank-management-system-yqrb.onrender.com)*

## 🚀 Installation & Setup

Follow these steps to set up the project locally:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/amar-bank.git
cd amar-bank
```

### 2️⃣ Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate   # For Mac/Linux
venv\Scripts\activate     # For Windows
pip install -r requirements.txt
```

### 3️⃣ Configure Environment Variables
Create a `.env` file and set up the necessary environment variables such as:
```env
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=your_postgresql_database_url
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 4️⃣ Apply Migrations & Run Server
```bash
python manage.py migrate
python manage.py runserver
```
Now, open your browser and visit **http://127.0.0.1:8000/** to access Amar Bank.

## 📜 License
This project is licensed under the **MIT License**.

## 🤝 Contributing
Contributions are welcome! Feel free to **fork** this repository and submit a **pull request**.

## 📩 Contact
📧 Email: durjoykumar177@gmail.com  
🐙 GitHub: [https://github.com/DurjoyKumar177/](#)

---
💡 *Built with Django & Love ❤️*

