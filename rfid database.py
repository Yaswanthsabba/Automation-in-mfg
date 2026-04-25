import pandas as pd
import datetime
import random

warehouse_size = 4
shelf_rows = 3
shelf_columns = 10

# Initialize set to store generated tag IDs
generated_tag_ids = set()

def generate_unique_tag_id():
    global generated_tag_ids
    tag_id = str(random.randint(100000, 1000000))
    while tag_id in generated_tag_ids:  # Check if the generated tag ID is already in use
        tag_id = str(random.randint(100000, 1000000))  # Generate a new tag ID
    generated_tag_ids.add(tag_id)  # Add the generated tag ID to the set
    return tag_id

def get_next_shelf(current_shelf):
    return current_shelf % warehouse_size + 1

def placed_at_location(tag_id, batch_number, database):
    global warehouse_size, shelf_rows, shelf_columns
    current_shelf = 1  # Initialize the current shelf number
    if batch_number == 1 and len(database) == 0:
        shelf = current_shelf
        row = random.randint(1, shelf_rows)
        column = random.randint(1, shelf_columns)
    else:
        if len(database) == 0:
            shelf = current_shelf
            row = random.randint(1, shelf_rows)
            column = random.randint(1, shelf_columns)
        else:
            prev_location = database[-1][1]  # Changed index to 1 to access location instead of tag_id
            parts = prev_location.split(',')
            shelf = int(parts[0])
            row = int(parts[1])
            column = int(parts[2])
            
            # Check if all locations on the current shelf are occupied
            occupied_locations = [tag[1] for tag in database if tag[1].startswith(f"{shelf},")]
            if len(occupied_locations) == shelf_rows * shelf_columns:
                # All locations on the current shelf are occupied, move to the next shelf
                current_shelf = get_next_shelf(current_shelf)
                shelf = current_shelf
                # Reset row and column to the first position on the new shelf
                row = 1
                column = 1
            
            # Apply proximity rule with a limit on attempts
            max_attempts = 100  # Maximum attempts to find a unique location
            attempts = 0
            while attempts < max_attempts:
                row_offset = random.randint(-1, 1)
                column_offset = random.randint(-1, 1)
                new_row = row + row_offset
                new_column = column + column_offset
                if 1 <= new_row <= shelf_rows and 1 <= new_column <= shelf_columns:
                    new_location = f"{shelf},{new_row},{new_column}"
                    if new_location not in [tag[1] for tag in database]:
                        row = new_row
                        column = new_column
                        break
                attempts += 1
            if attempts == max_attempts:
                print(f"Unable to find a unique location for tag {tag_id}.")

                # Attempt to find a new location on any shelf
                all_locations = [(s, r, c) for s in range(1, warehouse_size + 1) for r in range(1, shelf_rows + 1) for c in range(1, shelf_columns + 1)]
                random.shuffle(all_locations)
                for new_shelf, new_row, new_column in all_locations:
                    new_location = f"{new_shelf},{new_row},{new_column}"
                    if new_location not in [tag[1] for tag in database]:
                        shelf = new_shelf
                        row = new_row
                        column = new_column
                        break
                else:
                    print(f"Unable to find a unique location based on existing tag's location for tag {tag_id}.")
    location = f"{shelf},{row},{column}"
    return location

def simulate_rfid_tag_tracking(q):
    global database
    database = []  # Initialize the database
    batch_number = 1
    process_queue = ["Wafer preparation(7)", "Layer deposition(7)", "Etching(7)", "Doping(7)", "Wait after doping(2)", "Cleaning(7)", "Wait after cleaning(1)", "Sorting(7)", "Testing(7)", "Packaging(7)", "shipped(0)"]
    start_date = datetime.date(2024, 5, 10)
    while batch_number <= q:
        for _ in range(10):  # Add 10 tags to each batch
            tag_id = generate_unique_tag_id()
            location = placed_at_location(tag_id, batch_number, database)
            row_data = [tag_id, location, batch_number]
            process_time = 0
            for process in process_queue:
                if process == process_queue[0]:  # First process starts immediately
                    row_data.append(start_date)
                else:
                    row_data.append(start_date + datetime.timedelta(days=process_time))  # Update the process date
                process_time += int(process.split("(")[1].strip(")"))
            database.append(row_data)
        batch_number += 1
        start_date += datetime.timedelta(days=7)  # Increment the start_date by 7 days

    # Convert database to DataFrame
    columns = ['Tag ID', 'Location', 'Batch'] + process_queue
    df = pd.DataFrame(database, columns=columns)
    print(df)

    # Save the data to an Excel file
    df.to_excel('warehouse_data_updated.xlsx', index=False)
    print("Data saved to warehouse_data_updated.xlsx")

simulate_rfid_tag_tracking(20)
