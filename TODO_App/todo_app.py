"""
A simple To-Do list application built with Reflex.

To Run This App:
1.  Ensure you have Python installed (3.8+ recommended).
2.  Install Reflex:
    pip install reflex
3.  Save this code as `rx_todo_app.py` (or any other name).
4.  Initialize the Reflex project (only needed once per directory):
    reflex init
    (You can accept the defaults when prompted)
5.  Run the app from your terminal in the same directory:
    reflex run
6.  Open your web browser to the URL provided (usually http://localhost:3000).
"""
import reflex as rx
from typing import List, Dict, Any
import datetime # Optional: to add timestamps

# Define the application state
class TodoState(rx.State):
    """
    Manages the state of the To-Do list application.
    Includes the list of tasks and the current input field value.
    """
    # The list of tasks. Each task is a dictionary.
    # Example: {"description": "Buy milk", "completed": False, "created_at": "..."}
    tasks: List[Dict[str, Any]] = []

    # The current value of the new task input field.
    new_task_description: str = ""

    # --- Event Handlers (State Methods) ---

    def add_task(self):
        """Adds a new task to the list if the input is not empty."""
        if not self.new_task_description.strip():
            # Optional: Add user feedback here if needed (e.g., using rx.toast)
            print("Task description cannot be empty.") # Log to console
            return # Prevent adding empty tasks

        # Add the new task to the list
        self.tasks.append({
            "description": self.new_task_description.strip(),
            "completed": False,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M") # Optional timestamp
        })

        # Clear the input field after adding
        self.new_task_description = ""

    def toggle_complete(self, task_to_toggle: Dict[str, Any]):
        """
        Toggles the completion status of a specific task.
        Reflex handles finding and updating the task in the list based on identity.
        """
        # Find the task in the list and update its 'completed' status
        # This works because Reflex tracks the state list elements
        for i, task in enumerate(self.tasks):
             # Comparing dictionaries directly might be fragile if timestamps differ slightly
             # A safer approach might be to add a unique ID or compare descriptions if unique
             if task["description"] == task_to_toggle["description"] and task["created_at"] == task_to_toggle["created_at"]:
                 self.tasks[i]["completed"] = not self.tasks[i]["completed"]
                 break # Exit loop once found and updated

    def delete_task(self, task_to_delete: Dict[str, Any]):
        """Removes a specific task from the list."""
        # Filter out the task to delete
        # Create a new list excluding the task to be deleted
        self.tasks = [
            task for task in self.tasks
            if not (task["description"] == task_to_delete["description"] and task["created_at"] == task_to_delete["created_at"])
        ]

    # --- Computed Properties (Optional) ---
    @rx.var
    def completed_tasks_count(self) -> int:
        """Returns the number of completed tasks."""
        return sum(1 for task in self.tasks if task["completed"])

    @rx.var
    def total_tasks_count(self) -> int:
        """Returns the total number of tasks."""
        return len(self.tasks)

# --- UI Components ---

def task_item(task: Dict[str, Any]) -> rx.Component:
    """
    Renders a single task item with checkbox, description, and delete button.
    """
    return rx.hstack(
        # Checkbox for completion status
        rx.checkbox(
            is_checked=task["completed"],
            # Use on_click for the parent hstack or a dedicated button/icon
            # Checkbox on_change might require more complex state handling
            # Let's use the hstack's click to toggle for simplicity here
            # Alternatively, add a dedicated toggle button/icon
            on_click=TodoState.toggle_complete(task), # Toggle on clicking the row
            size="lg", # Make checkbox bigger
            color_scheme="green",
            margin_right="1em",
        ),
        # Task description with conditional styling
        rx.text(
            task["description"],
            # Apply strikethrough if completed
            text_decoration=rx.cond(
                task["completed"], "line-through", "none"
            ),
            # Make text gray if completed
            color=rx.cond(
                task["completed"], "gray.600", "black"
            ),
            # Allow text to take available space
            flex_grow=1,
            # Handle clicks on text as well (optional redundancy)
            on_click=TodoState.toggle_complete(task),
            cursor="pointer", # Indicate clickable text
        ),
        # Delete button with an icon
        rx.icon_button(
            rx.icon(tag="delete", size=20), # Use Reflex's built-in delete icon
            on_click=TodoState.delete_task(task),
            color_scheme="red",
            variant="ghost", # Less prominent button style
            size="sm",
        ),
        # Styling for the row
        align_items="center", # Vertically align items in the middle
        width="100%",
        padding_y="0.5em", # Add vertical padding
        border_bottom="1px solid #eee", # Separator line
    )

# --- Main Page Layout ---

def index() -> rx.Component:
    """
    The main page layout for the To-Do application.
    """
    return rx.container( # Center content and limit width
        rx.vstack(
            # App Title
            rx.heading("📝 Reflex To-Do List", size="xl", margin_bottom="1em", text_align="center"),

            # Input form for adding new tasks
            rx.hstack(
                rx.input(
                    placeholder="What needs to be done?",
                    value=TodoState.new_task_description,
                    on_change=TodoState.set_new_task_description, # Update state variable on input change
                    on_key_down=rx.cond( # Allow adding task by pressing Enter
                         TodoState.new_task_description.strip() != "", # Only if input is not empty
                         rx.call_script(
                             """
                             if (event.key === 'Enter') {
                                 document.getElementById('add-task-button').click();
                                 event.preventDefault(); // Prevent default form submission if any
                             }
                             """
                         ),
                         None # Do nothing if input is empty
                     ),
                    flex_grow=1, # Allow input to expand
                    size="lg",
                ),
                rx.button(
                    "Add Task",
                    id="add-task-button", # ID for the Enter key script
                    on_click=TodoState.add_task,
                    size="lg",
                    color_scheme="blue",
                    # Disable button if input is empty
                    is_disabled=TodoState.new_task_description.strip() == "",
                ),
                width="100%",
                margin_bottom="1.5em",
            ),

            # Display the list of tasks
            rx.heading("Current Tasks", size="lg", margin_bottom="0.5em"),
            rx.cond( # Show message if no tasks
                TodoState.tasks,
                rx.vstack(
                    # Iterate over tasks and render each item using the task_item function
                    rx.foreach(TodoState.tasks, task_item),
                    align_items="stretch", # Ensure items take full width
                    width="100%",
                ),
                rx.center( # Center the "no tasks" message
                    rx.text("No tasks yet. Add some above! 🎉", color="gray.500"),
                    padding="2em",
                    width="100%",
                )
            ),

            # Optional: Task Summary
            rx.divider(margin_y="1.5em"),
            rx.hstack(
                 rx.text(f"Total Tasks: {TodoState.total_tasks_count}"),
                 rx.spacer(), # Pushes items apart
                 rx.text(f"Completed: {TodoState.completed_tasks_count}", color="green.600"),
                 width="100%",
                 justify="space-between", # Ensure space between elements
                 padding_x="0.5em",
            ),

            # Overall alignment and spacing for the main vstack
            align_items="stretch", # Stretch children to container width
            spacing="1em", # Spacing between elements in the vstack
            width="100%",
        ),
        # Container styling
        max_width="600px", # Limit the maximum width of the content
        padding="2em",
        margin_top="2em",
        border="1px solid #ddd",
        border_radius="lg",
        box_shadow="md",
    )


# --- App Setup ---
# Create the Reflex application instance
app = rx.App(
    state=TodoState,
    # Optional: Add stylesheets or themes
    # stylesheets=[
    #     "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css", # Example for icons
    # ],
    # theme=rx.theme(appearance="light")
)

# Add the main page to the app
app.add_page(index, title="Reflex To-Do App")

# The following line is not needed when running with `reflex run`,
# but it's standard practice in Reflex examples.
# The `reflex run` command handles compilation and serving.
app.compile()
