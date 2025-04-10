import reflex as rx
from typing import List, Optional

# Define the state
class TodoState(rx.State):
    # The list of todo items
    todos: List[dict] = []
    # The current todo being added
    new_todo: str = ""
    # The filter status
    filter_status: str = "all"

    def add_todo(self):
        if self.new_todo.strip() != "":
            self.todos.append({"text": self.new_todo, "completed": False})
            self.new_todo = ""

    def toggle_todo(self, index: int):
        self.todos[index]["completed"] = not self.todos[index]["completed"]

    def delete_todo(self, index: int):
        self.todos.pop(index)

    def clear_completed(self):
        self.todos = [todo for todo in self.todos if not todo["completed"]]

    @rx.var
    def filtered_todos(self) -> List[dict]:
        if self.filter_status == "active":
            return [todo for todo in self.todos if not todo["completed"]]
        elif self.filter_status == "completed":
            return [todo for todo in self.todos if todo["completed"]]
        return self.todos

    def set_filter(self, status: str):
        self.filter_status = status


# Define the UI components
def todo_item(todo: dict, index: int):
    return rx.hstack(
        rx.checkbox(
            is_checked=todo["completed"],
            on_change=lambda: TodoState.toggle_todo(index),
        ),
        rx.text(
            todo["text"],
            text_decoration="line-through" if todo["completed"] else "none",
            flex_grow=1,
        ),
        rx.button(
            "Delete",
            on_click=lambda: TodoState.delete_todo(index),
            color_scheme="red",
            size="sm",
        ),
        width="100%",
        padding="2",
        border_bottom="1px solid #eaeaea",
    )


def index():
    return rx.container(
        rx.vstack(
            rx.heading("Todo App", size="2", margin_bottom="4"),  # Changed size from "lg" to "2"
            rx.hstack(
                rx.input(
                    placeholder="Add a new todo...",
                    value=TodoState.new_todo,
                    on_change=TodoState.set_new_todo,
                    width="100%",
                ),
                rx.button("Add", on_click=TodoState.add_todo),
                width="100%",
            ),
            rx.box(
                rx.foreach(
                    TodoState.filtered_todos,
                    lambda todo, index: todo_item(todo, index),
                ),
                width="100%",
                margin_top="4",
                border="1px solid #eaeaea",
                border_radius="md",
            ),
            rx.hstack(
                rx.text(f"{len(TodoState.todos)} items"),
                rx.spacer(),
                rx.button(
                    "All",
                    on_click=lambda: TodoState.set_filter("all"),
                    color_scheme="blue" if TodoState.filter_status == "all" else "gray",
                    size="sm",
                ),
                rx.button(
                    "Active",
                    on_click=lambda: TodoState.set_filter("active"),
                    color_scheme="blue" if TodoState.filter_status == "active" else "gray",
                    size="sm",
                ),
                rx.button(
                    "Completed",
                    on_click=lambda: TodoState.set_filter("completed"),
                    color_scheme="blue" if TodoState.filter_status == "completed" else "gray",
                    size="sm",
                ),
                rx.spacer(),
                rx.button(
                    "Clear Completed",
                    on_click=TodoState.clear_completed,
                    size="sm",
                ),
                width="100%",
                padding="2",
            ),
            width="100%",
            max_width="600px",
            margin="0 auto",
            padding="4",
        )
    )


# Create the app
app = rx.App()
app.add_page(index)

# Run the app
if __name__ == "__main__":
    app.compile()
