# %%
import tkinter as tk # for create GUI
from tkinter import simpledialog, messagebox, ttk # foe input dialog and message
import pandas as pd # for handle CSV data
from rapidfuzz import fuzz, process # for fuzzy string matching
import requests
import math

# Define the CustomDialog class using sliders for user input
class CustomDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Enter your age (years):").grid(row=0)
        tk.Label(master, text="Enter your gender:").grid(row=1)
        tk.Label(master, text="Enter your weight (kg):").grid(row=2)
        tk.Label(master, text="Enter your height (cm):").grid(row=3)
        tk.Label(master, text="Enter your activity level:").grid(row=4)

        self.age = tk.Scale(master, from_=0, to=120, orient=tk.HORIZONTAL)
        self.age.grid(row=0, column=1)

        self.gender_var = tk.StringVar()
        self.gender_var.set("male")
        tk.Radiobutton(master, text="Male", variable=self.gender_var, value="male").grid(row=1, column=1)
        tk.Radiobutton(master, text="Female", variable=self.gender_var, value="female").grid(row=1, column=2)

        self.weight = tk.Scale(master, from_=0, to=200, orient=tk.HORIZONTAL)
        self.weight.grid(row=2, column=1)

        self.height = tk.Scale(master, from_=0, to=250, orient=tk.HORIZONTAL)
        self.height.grid(row=3, column=1)

        self.activity_level = ttk.Combobox(master, values=["sedentary", "light", "moderate", "active"])
        self.activity_level.grid(row=4, column=1)
        self.activity_level.current(0)

        return self.age  # initial focus

    def apply(self):
        self.result = {
            "age": self.age.get(),
            "gender": self.gender_var.get(),
            "weight": self.weight.get(),
            "height": self.height.get(),
            "activity_level": self.activity_level.get()
        }


# define the CalorieApp class, inheriting from tkinter's Tk class to create the main window
class CalorieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Calorie Calculator')
        self.geometry('400x600') # set the size of the window

        # initialize total calories and eaten calories
        self.total_calories_goal = 1300 # daily calorie goal,adjustable
        self.eaten_calories = 0 # variable to track the number of calories eaten
        self.burned_calories = 300 # static value for now

        # 1. Add Canvas for Circular Progress Ring
        self.progress_canvas = tk.Canvas(self, width=200, height=200)
        self.progress_canvas.pack(pady=20)
        self.progress_circle = self.progress_canvas.create_arc(
            10, 10, 190, 190, start=90, extent=0, fill="green"
        )  # Circular progress arc
        self.progress_label = tk.Label(self, text="Remaining\n100%", font=("Arial", 16))
        self.progress_label.pack()



        # top sevtion with calories left and burned
        self.top_frame = tk.Frame(self) # create a frame to hold the top section
        self.top_frame.pack(pady=10) # for better spacing

        # label to show eaten calories
        self.eaten_label = tk.Label(self.top_frame, text=f'{self.eaten_calories} eaten', font=('Arial', 16))
        self.eaten_label.grid(row=0, column=0, padx =20) # place it in the grid at row 0, column 0

        # create a frame to display the calories left
        self.cal_left_frame = tk.Frame(self.top_frame, width=100, height=100)
        self.cal_left_frame.grid(row=0, column=1)
        # label to display tje calories left = total goal - eaten calories
        self.cal_left_label = tk.Label(self.cal_left_frame, text=f'{self.total_calories_goal - self.eaten_calories}\ncal left', font=('Ariel', 18), fg="black", width=10, height=3)
        self.cal_left_label.grid(row=0, column=1) # palce it in the middle of the top frame

        # label to show burned calories
        self.burned_label = tk.Label(self.top_frame, text=f"{self.burned_calories} burned", font=("Arial", 16))
        self.burned_label.grid(row=0, column=2, padx=20)

        # macronutrients row (carbs, protein, fat)
        self.macros_frame = tk.Frame(self)  # create a frame to hold the macronutrient labels
        self.macros_frame.pack(pady=10)

        # label for carbs
        self.carbs_label = tk.Label(self.macros_frame, text="carbs", font=("Arial", 14))
        self.carbs_label.grid(row=0, column=0, padx=20)  # place it in the grid at row 0, column 0

        # label for protein
        self.protein_label = tk.Label(self.macros_frame, text="protein", font=("Arial", 14))
        self.protein_label.grid(row=0, column=1, padx=20) 

        # label for fat
        self.fat_label = tk.Label(self.macros_frame, text="fat", font=("Arial", 14))
        self.fat_label.grid(row=0, column=2, padx=20) 

        # meal buttons (breakfast, lunch, dinner, snack)
        self.meals_frame = tk.Frame(self)  # create a frame to hold the meal buttons
        self.meals_frame.pack(pady=10)

        # button for breakfast, calls search_food with "breakfast" as the argument
        self.breakfast_button = tk.Button(self.meals_frame, text="☕ breakfast", font=("Arial", 14), command=lambda: self.search_food("breakfast"))
        self.breakfast_button.grid(row=0, column=0, pady=10, ipadx=10) 

        # button for lunch, calls search_food with "lunch" as the argument
        self.lunch_button = tk.Button(self.meals_frame, text="🍱 lunch", font=("Arial", 14), command=lambda: self.search_food("lunch"))
        self.lunch_button.grid(row=1, column=0, pady=10, ipadx=10) 

        # button for dinner, calls search_food with "dinner" as the argument
        self.dinner_button = tk.Button(self.meals_frame, text="🥗 dinner", font=("Arial", 14), command=lambda: self.search_food("dinner"))
        self.dinner_button.grid(row=2, column=0, pady=10, ipadx=10)

        # button for snack, calls search_food with "snack" as the argument
        self.snack_button = tk.Button(self.meals_frame, text="🍎 snack", font=("Arial", 14), command=lambda: self.search_food("snack"))
        self.snack_button.grid(row=3, column=0, pady=10, ipadx=10) 

        # home button, can be used for future navigation
        self.home_button = tk.Button(self, text="🏠", font=("Arial", 18))
        self.home_button.pack(pady=20)


        # button for calculate BMR
        self.bmr_button = tk.Button(self, text="Calculate BMR & Daily Calories", command=self.calculate_bmr)
        self.bmr_button.pack(pady=20)

        # read the calorie data drom the CSV file
        # self.df = pd.read_csv('calories.csv')

        # API key
        self.api_ninjas_key = 'ksu4AKLo3pNnpy7RnxzjOg==qM78rW83uDKTvkTu'  

    def calculate_bmr(self):
        # Use CustomDialog to collect user input
        dialog = CustomDialog(self, "Input Details")
        if dialog.result:  
            user_input = dialog.result
            age = user_input["age"]
            gender = user_input["gender"]
            weight = user_input["weight"]
            height = user_input["height"]
            activity_level = user_input["activity_level"]

            # Calculate BMR
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            elif gender == "female":
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            else:
                messagebox.showinfo("Error", "Invalid gender input!")
                return

            # Calculate daily calorie needs based on activity level
            activity_multiplier = {
                "sedentary": 1.2,
                "light": 1.375,
                "moderate": 1.55,
                "active": 1.725
            }

            if activity_level in activity_multiplier:
                daily_calories = bmr * activity_multiplier[activity_level]
                self.total_calories_goal = daily_calories  # Update the total calorie goal
                messagebox.showinfo("Daily Calorie Needs", f"You need approximately {daily_calories:.0f} calories per day.")
                self.update_calories_display()  # Update the calories left display
            else:
                messagebox.showinfo("Error", "Invalid activity level input!")



    def edamam_nutrition_data(self, food):
        """extracts nutrition data from the Edamam Nutrition API
        Args:
            food (str): the food item to get nutrition data for
        Returns:
            dict: a dictionary containing the nutrition data or None if the request was unsuccessful
        """
        # get API app_id and app_key from keys.py
        from keys import edamam_app_id, edamam_app_key
        
        api_url = "https://api.edamam.com/api/nutrition-data"

        # Make a request to the Edamam Nutrition API
        response = requests.get(api_url, params={
            "app_id": edamam_app_id,
            "app_key": edamam_app_key,
            "ingr": food
        })

        food_data = {}

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            calories = data.get('calories', 0)
            protein = data['totalNutrients'].get('PROCNT', {}).get('quantity', 0)
            carbohydrate = data['totalNutrients'].get('CHOCDF', {}).get('quantity', 0)
            fat = data['totalNutrients'].get('FAT', {}).get('quantity', 0)
            sugar = data['totalNutrients'].get('SUGAR', {}).get('quantity', 0)
            total_weight = data.get('totalWeight', 0)

            # add data to a dictionary called food_data
            # and convert values to integers
            food_data = {
                "calories": int(calories),
                "total_weight": int(total_weight),
                "protein": int(protein),
                "carbohydrate": int(carbohydrate),
                "fat": int(fat),
                "sugar": int(sugar)
            }
            return food_data
        else:
            print(f"Error: Unable to fetch data (status code: {response.status_code})")
            return None
    
    # function to handle food search for each meal
    def search_food(self, meal):
        search_term = simpledialog.askstring('input', f'Enter food item for {meal} with number or weight:') # ask user for the food item to search for
        if not search_term:
            return # if no input, exit the fuction
        
        food_data = self.edamam_nutrition_data(search_term) # request food data from API

        calories = food_data.get('calories', 0) # total calories for given number/weight of food
        protein = food_data.get('protein', 0)
        carbs = food_data.get('carbohydrate', 0)
        fat = food_data.get('fat', 0)
        
        if calories * protein * carbs * fat > 0: # did we get any non-0 data?
            # show calorie info
            messagebox.showinfo("Food Info", f"Calories: {calories}\nProtein: {protein}g\nCarbs: {carbs}g\nFat: {fat}g")
            #self.process_food_selection(search_term, calories)

            # update the eaten calories and recalculate the calories left
            self.eaten_calories += calories
            self.update_calories_display() # update the GUI display with new values

        else:
            messagebox.showinfo("No Match", f"No nutritional data found for {search_term}!")



    # function to process the selected food item after matching
    def process_food_selection(self, food_item, calories):
        # row = self.df.iloc[index]
        # ask the user for the weight or portion size of the food
        weight = simpledialog.askfloat('input', f"Enter the weight in grams for {food_item}: ")
        if weight is None:  # default to 100 grams if no input
            weight = 100

        # calculate total calories based on the portion size
        total_calories = (calories * weight)/100

        # update the eaten calories and recalculate the calories left
        self.eaten_calories += total_calories
        self.update_calories_display() # update the GUI display with new values

    # function to update the calorie-related labels in the GUI
    def update_calories_display(self):
        cal_left = max(0, self.total_calories_goal - self.eaten_calories)
        percentage = (cal_left / self.total_calories_goal) * 100 if self.total_calories_goal > 0 else 0
        self.cal_left_label.config(text=f"{cal_left:.0f}\ncal left")
        self.eaten_label.config(text=f"{self.eaten_calories:.0f} eaten")

        # Update circular progress ring
        extent = (percentage / 100) * -360  # clockwise
        self.progress_canvas.itemconfig(self.progress_circle, extent=extent)
        self.progress_label.config(text=f"Remaining\n{percentage:.0f}%")

        # Trigger an alert if calories exceeded
        if self.eaten_calories > self.total_calories_goal:
            messagebox.showwarning("Calorie Limit Exceeded", "You have exceeded your daily calorie limit!")

        
app = CalorieApp()
app.mainloop()


