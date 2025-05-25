# 🏥 Patient Management System

A secure, role-based web application designed to manage doctors, patients, and medical reports in healthcare environments. This system supports multiple user types — Admin, Doctor, and Patient — enabling tailored access and workflows for hospital staff and patients.

---

## 🚀 Project Overview

This system provides a centralized, secure platform where different users can manage or access medical data based on their roles. Admins can manage doctors and patients, doctors can view and update their patients’ information and medical reports, and patients can view their own reports.

Built with **Python (Flask)** and **MySQL**, it showcases role-based authentication and dynamic data management for healthcare institutions.

---

## 💻 Tech Stack

| Technology                 | Purpose                             |
| -------------------------- | ----------------------------------- |
| **Python (Flask)**         | Backend Web Framework               |
| **MySQL**                  | Database Management                 |
| **HTML / CSS / Bootstrap** | Frontend UI                         |
| **Flask-Login**            | Authentication & Session Management |
| **mysql-connector-python** | Database Connector                  |

---

## 📂 Features

✅ Role-based Authentication (Admin, Doctor, Patient)
✅ Secure Login and Logout System
✅ Doctor Management (Add, Update, View) — Admin Access
✅ Patient Management (Add, Assign Doctor, Update) — Admin Access
✅ Medical Reports Management (Add, Update, View) — Doctor & Patient Access
✅ Dynamic Dashboards Based on User Role
✅ Search and Sorting Functionality for Efficient Data Retrieval

---

## 🗂 Database Design

| Table Name       | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `users`          | Stores user credentials and roles (Admin, Doctor, Patient). |
| `Doctors`        | Contains detailed information about doctors.                |
| `Patients`       | Stores patient information linked to assigned doctors.      |
| `MedicalReports` | Holds diagnostic medical reports related to patients.       |

**Relationships:**

* One **user** can have a specific role: Admin, Doctor, or Patient.
* Each **doctor** (user with role 'Doctor') manages multiple **patients**.
* Each **patient** (user with role 'Patient') can have multiple **medical reports**.

---

## 🔐 Default Admin Credentials

| Username | Password   |
| -------- | ---------- |
| `admin`  | `password` |

---

## 🧠 Future Improvements

* Multi-factor authentication and enhanced security features.
* Role-specific dashboards with custom functionalities.
* Patient self-service portal for appointments and reports.
* Integration of notification systems (email/SMS).
* AI/ML integration for predictive healthcare analytics.

---


