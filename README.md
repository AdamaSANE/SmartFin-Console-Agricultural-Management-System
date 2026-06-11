# 🌾 SmartFin - Agricultural Management System

A console-based agricultural management system designed to manage crop inventory and farm finances.

## 📋 Features

- **Inventory Management**: Add and track harvests (quantities in kg)
- **Financial Management**: Record income (sales) and expenses (fertilizers, seeds, etc.)
- **Reporting**: Generate summary reports with stock status and financial information
- **Net Profit Calculation**: Automatically determine profit (income - expenses)

## 🚀 Usage

### Running the Program

```bash
python SmartFin_Console_Agricultural.py
```

### Menu Options

1. **Add a new harvest**: Enter the crop name and quantity in kg
2. **Record a financial transaction**:
   - A: Income (Sale)
   - B: Expense (Fertilizer, seeds, etc.)
3. **Generate a summary report**: Displays inventory and financial status
4. **Quit**: Close the program

## 💾 Data Structure

- **Inventory**: Dictionary storing crops and their quantities (in kg)
- **Finances**: Dictionary containing total income and expenses (in FCFA)

## 📊 Sample Report

```
────────────────────────────────────────
📊 SUMMARY REPORT 📊
────────────────────────────────────────

📦 INVENTORY STATUS:
- Tomatoes: 250 kg
- Onions: 150 kg

💰 FINANCIAL SUMMARY:
- Total Income: 500000 FCFA
- Total Expenses: 150000 FCFA

=> NET PROFIT: 350000 FCFA
────────────────────────────────────────
```

## 🛠️ Error Handling

- Validation of numeric inputs for quantities and amounts
- Clear error messages for invalid input
- Handling of duplicate crops (adds to existing quantity)

## 📝 Learning Outcomes

This project demonstrates:

- Use of data structures (dictionaries)
- Exception handling (try/except)
- Function-oriented programming
- Loops and conditional statements
- Console-based user interface

---

**Stanford 2026 Project - Agricultural Management System**
