def display_menu():
    print("\n" + "="*40)
    print("🌾 AGRICULTURAL MANAGEMENT SYSTEM 🌾")
    print("="*40)
    print("1. Add a new harvest (Stock)")
    print("2. Record a financial transaction")
    print("3. Generate summary report")
    print("4. Quit")
    print("="*40)

def add_harvest(inventory):
    crop = input("Enter the crop name (e.g., Onions, Tomatoes): ").capitalize()
    
    # Ensure the user enters a valid number
    try:
        quantity = float(input(f"Enter the harvested quantity for {crop} (in kg): "))
    except ValueError:
        print("Error: Please enter a valid number.")
        return # Return to the main menu in case of an error
        
    # If the crop already exists, add to the existing quantity; otherwise, create it
    if crop in inventory:
        inventory[crop] += quantity
    else:
        inventory[crop] = quantity
        
    print(f"✅ Success: {quantity} kg of {crop} added to the stock.")

def add_transaction(finances):
    print("\nTransaction type:")
    print("A. Income (Sale)")
    print("B. Expense (Fertilizer, seeds, etc.)")
    choice = input("Your choice (A or B): ").upper()
    
    try:
        amount = float(input("Enter the amount (in FCFA): "))
    except ValueError:
        print("Error: Please enter a valid amount.")
        return
        
    if choice == 'A':
        finances['income'] += amount
        print(f"✅ Success: Income of {amount} FCFA recorded.")
    elif choice == 'B':
        finances['expenses'] += amount
        print(f"✅ Success: Expense of {amount} FCFA recorded.")
    else:
        print("Invalid choice.")

def generate_report(inventory, finances):
    print("\n" + "-"*40)
    print("📊 SUMMARY REPORT 📊")
    print("-"*40)
    
    print("\n📦 INVENTORY STATUS:")
    if not inventory: # Checks if the dictionary is empty
        print("The inventory is empty.")
    else:
        for crop in inventory:
            print(f"- {crop}: {inventory[crop]} kg")
            
    print("\n💰 FINANCIAL SUMMARY:")
    print(f"- Total Income: {finances['income']} FCFA")
    print(f"- Total Expenses: {finances['expenses']} FCFA")
    
    net_profit = finances['income'] - finances['expenses']
    print(f"\n=> NET PROFIT: {net_profit} FCFA")
    print("-"*40)

def main():
    # Initialization of our data structures (dictionaries)
    agricultural_inventory = {}
    farm_finances = {'income': 0.0, 'expenses': 0.0}
    
    # Main program loop
    while True:
        display_menu()
        user_choice = input("What would you like to do? (1-4): ")
        
        if user_choice == '1':
            add_harvest(agricultural_inventory)
        elif user_choice == '2':
            add_transaction(farm_finances)
        elif user_choice == '3':
            generate_report(agricultural_inventory, farm_finances)
        elif user_choice == '4':
            print("Thank you for using the management system. See you soon!")
            break
        else:
            print("Unrecognized option. Please type 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()