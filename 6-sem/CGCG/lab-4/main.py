from PIL import Image, ImageDraw, ImageFont

# Create a blank image with white background
width, height = 1200, 900
image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)

# Define colors and font
black = "black"
gray = "gray"
blue = "blue"
red = "red"
font = ImageFont.load_default()

# Draw main sections
draw.rectangle([(20, 20), (580, 150)], outline=black, width=3)
draw.text((30, 30), "Use Cases", fill=black, font=font)
use_cases = [
    "1. Hire a Personal Trainer",
    "2. Book a Class",
    "3. Find a Workout Partner",
    "4. Buy a Gym Membership",
    "5. Register for or Organize a Tournament",
    "6. Track Records/Achievements",
    "7. Share Tips / Maintain a Blog",
    "8. Purchase Sports Equipment",
]
for i, use_case in enumerate(use_cases):
    draw.text((40, 50 + 10 * i), use_case, fill=gray, font=font)

draw.rectangle([(620, 20), (1180, 400)], outline=black, width=3)
draw.text((630, 30), "Pages and Features", fill=black, font=font)

pages_features = [
    ("Home Page", ["Trainer Rating", "Photo", "Nickname + Full Name", "Training Types", "Location", "Languages",
                   "Trainer's Blog", "Schedule Button", "Pricing Button", "Contact Button"]),
    ("Rating System", ["Post-Training Rating", "Session Count", "Average Rating"]),
    ("Nickname", ["Uniqueness", "Restrictions", "Visibility"]),
    ("Location", ["Google Map Pinpoint"]),
    ("Blog", ["Post Creation", "Visibility", "Sharing"]),
    ("Calendar", ["Set Training Times", "Cancel Sessions", "Participant Limit", "Subscription Options", "Book Sessions",
                  "Cancel Booking", "View Participants"]),
    ("Pricing List", ["Training Types", "Discounts"]),
    ("Contact Trainer", ["Direct Message", "Group Creation"]),
]

y_start = 50
for title, features in pages_features:
    draw.text((630, y_start), title, fill=blue, font=font)
    for j, feature in enumerate(features):
        draw.text((650, y_start + 10 * (j + 1)), feature, fill=gray, font=font)
    y_start += 15 * (len(features) + 1)

draw.rectangle([(20, 170), (580, 400)], outline=black, width=3)
draw.text((30, 180), "Filters", fill=black, font=font)

filters = [
    ("Find a Personal Trainer", ["Country/City", "Training Type", "Day and Time", "Sport Type", "Cost", "Gender",
                                 "Trainer Rating", "Trainer Language Proficiency"]),
    ("Find a Class", ["Country/City", "Training Type", "Day and Time", "Sport Type", "Cost", "Gender", "Trainer Rating",
                      "Max/Min Participants", "Age Category/Level", "Trainer Language Proficiency"]),
    ("Find Tournaments/Competitions", ["Tournament Name Search", "Sport Type", "Date and Time", "Participation Cost",
                                       "Location (Country, City)", "Number of Participants"]),
    ("Find a Workout Partner", ["Country/City", "Language", "Training Type", "Age", "Gender", "Training Days and Time",
                                "Experience Level"]),
]

y_start = 200
for title, filters_list in filters:
    draw.text((30, y_start), title, fill=blue, font=font)
    for j, filter_item in enumerate(filters_list):
        draw.text((50, y_start + 10 * (j + 1)), filter_item, fill=gray, font=font)
    y_start += 15 * (len(filters_list) + 1)

draw.rectangle([(20, 420), (580, 500)], outline=black, width=3)
draw.text((30, 430), "Main Menu", fill=black, font=font)
main_menu = ["View Profile", "Find a Personal Trainer", "Find a Class", "Find a Tournament/Competition", "Find a Workout Partner"]
for i, item in enumerate(main_menu):
    draw.text((40, 450 + 10 * i), item, fill=gray, font=font)

# Save the image
image_path = "web_application_plan_example.png"
image.save(image_path)
image.show()

image_path
