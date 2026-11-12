from dataclasses import dataclass
from drafter import *
from drafter.testing import assert_state, assert_has
from bakery import assert_equal

### Dataclasses

@dataclass
class Book:
    """Stores info about one book."""
    title: str
    author: str
    genre: str
    status: str
    rating: int
    review: str


@dataclass
class State:
    """Stores info shared across the entire website."""
    books: list[Book]
    reading_goal: int
    current_page: str
    active_filter: str
    selected_book: int
    message: str

### Helper Functions

def count_finished(books: list[Book]) -> int:
    """Counts # of books that have been finished."""
    total = 0

    for book in books:
        if book.status == "Finished":
            total += 1

    return total


def count_reading(books: list[Book]) -> int:
    """Counts # of books currently being read."""
    total = 0

    for book in books:
        if book.status == "Currently Reading":
            total += 1

    return total


def count_want_to_read(books: list[Book]) -> int:
    """Counts # of books the user wants to read."""
    total = 0

    for book in books:
        if book.status == "Want to Read":
            total += 1

    return total


def find_duplicate(
    books: list[Book],
    title: str,
    author: str
) -> bool:
    """Checks if a book with this title AND author exists."""
    for book in books:
        if (book.title.lower() == title.lower()
                and book.author.lower() == author.lower()):
            return True

    return False


def navigation(state: State) -> list:
    """Creates navigation links for each page."""
    return [
        Button("Home", "index"),
        Button("My Bookshelf", "bookshelf"),
        Button("Add a Book", "add_book"),
        Button("Statistics", "statistics"),
        HorizontalRule()
    ]

### Routes

# Home Page

@route
def index(state: State) -> Page:
    """Displays the homepage and reading progress."""
    state.current_page = "Home"

    finished = count_finished(state.books)
    currently_reading = count_reading(state.books)

    if state.reading_goal > 0:
        remaining = state.reading_goal - finished
    else:
        remaining = 0

    if remaining <= 0 and state.reading_goal > 0:
        goal_message = "You reached your goal!"
    else:
        goal_message = "Keep reading!"

    return Page(state, [
        Header("Archive of Your Own"),
        "Your personal digital bookshelf.",
        HorizontalRule(),

        *navigation(state),

        Header("Welcome back!"),
        "Total books: " + str(len(state.books)),
        "Books finished: " + str(finished),
        "Currently reading: " + str(currently_reading),
        "Yearly reading goal: " + str(state.reading_goal),

        goal_message,
        "Books until goal: "
        + str(max(0, remaining)),

        HorizontalRule(),
        Header("Recently Added Books"),

        *[
            book.title + " by " + book.author
            for book in state.books[-3:]
        ],

        Button("My Bookshelf", "bookshelf"),
        Button("Add a New Book", "add_book"),
        Button("View Reading Statistics", "statistics")
    ])

# Bookshelf Page

@route
def bookshelf(state: State) -> Page:
    """Displays books based on the selected filter."""
    state.current_page = "Bookshelf"

    content = [
        Header("My Bookshelf"),
        *navigation(state),
        "Choose a category to organize your books.",

        Button(
            "All Books",
            "change_filter",
            {"chosen_filter": "All Books"}
        ),
        Button(
            "Want to Read",
            "change_filter",
            {"chosen_filter": "Want to Read"}
        ),
        Button(
            "Currently Reading",
            "change_filter",
            {"chosen_filter": "Currently Reading"}
        ),
        Button(
            "Finished",
            "change_filter",
            {"chosen_filter": "Finished"}
        ),
        HorizontalRule()
    ]

    displayed_books = 0

    for index, book in enumerate(state.books):

        if (state.active_filter == "All Books"
                or book.status == state.active_filter):

            displayed_books += 1

            content.extend([
                Header(book.title, 3),
                "Author: " + book.author,
                "Genre: " + book.genre,
                "Status: " + book.status,
                "Rating: " + str(book.rating) + "/5 stars",

                Button(
                    "View Details",
                    "book_details",
                    {"book_id": index}
                ),
                HorizontalRule()
            ])

    if displayed_books == 0:
        content.append("No books found in this category.")

    content.append(Button("Add a Book", "add_book"))
    content.append(Button("Home", "index"))

    return Page(state, content)

# Change Bookshelf Filter

@route
def change_filter(state: State, chosen_filter: str) -> Page:
    """Updates the bookshelf filter."""
    state.active_filter = chosen_filter
    state.message = "Showing: " + chosen_filter

    return bookshelf(state)


# Add Book

@route
def add_book(state: State) -> Page:
    """Displays the form used to enter a new book."""
    state.current_page = "Add Book"

    return Page(state, [
        Header("Add a New Book"),
        *navigation(state),

        "Enter the information about your book.",

        "Book Title:",
        TextBox("title"),

        "Author:",
        TextBox("author"),

        "Genre:",
        SelectBox(
            "genre",
            [
                "Fantasy",
                "Romance",
                "Mystery",
                "Science Fiction",
                "Nonfiction",
                "Horror",
                "Other"
            ]
        ),

        "Reading Status:",
        SelectBox(
            "status",
            [
                "Want to Read",
                "Currently Reading",
                "Finished"
            ]
        ),

        "Rating:",
        SelectBox(
            "rating",
            ["0", "1", "2", "3", "4", "5"]
        ),

        "Review:",
        TextArea("review"),

        Button("Save Book", "save_book"),
        Button("Cancel", "bookshelf")
    ])

# Save Book

@route
def save_book(
    state: State,
    title: str,
    author: str,
    genre: str,
    status: str,
    rating: str,
    review: str
) -> Page:
    """Confirms and saves a new book."""
    if title.strip() == "" or author.strip() == "":
        state.message = "Please enter a title and author."
        return add_book(state)

    if find_duplicate(state.books, title.strip(), author.strip()):
        state.message = "This book is already in your bookshelf."
        return add_book(state)

    new_book = Book(
        title.strip(),
        author.strip(),
        genre,
        status,
        int(rating),
        review.strip()
    )

    state.books.append(new_book)
    state.message = "Your book was added successfully!"
    state.active_filter = "All Books"

    return bookshelf(state)

# Book Details

@route
def book_details(state: State, book_id: int) -> Page:
    """Displays info about the selected book."""
    if book_id < 0 or book_id >= len(state.books):
        state.message = "Book could not be found."
        return bookshelf(state)

    state.selected_book = book_id
    state.current_page = "Book Details"

    book = state.books[book_id]

    return Page(state, [
        Header("Book Details"),
        *navigation(state),

        Header(book.title),
        "Author: " + book.author,
        "Genre: " + book.genre,
        "Reading Status: " + book.status,
        "Rating: " + str(book.rating) + "/5",
        Header("My Review", 3),
        book.review if book.review else "No review written yet.",

        Button(
            "Edit Book",
            "edit_book",
            {"book_id": book_id}
        ),

        Button(
            "Delete Book",
            "delete_book",
            {"book_id": book_id}
        ),

        Button("Back to Bookshelf", "bookshelf")
    ])

# Edit Book

@route
def edit_book(state: State, book_id: int) -> Page:
    """Displays a form used to edit an existing book."""
    if book_id < 0 or book_id >= len(state.books):
        state.message = "Book could not be found."
        return bookshelf(state)

    state.selected_book = book_id
    state.current_page = "Edit Book"

    book = state.books[book_id]

    return Page(state, [
        Header("Edit Book"),
        *navigation(state),

        "Book Title:",
        TextBox("title", book.title),

        "Author:",
        TextBox("author", book.author),

        "Genre:",
        SelectBox(
            "genre",
            [
                "Fantasy",
                "Romance",
                "Mystery",
                "Science Fiction",
                "Nonfiction",
                "Horror",
                "Other"
            ],
            book.genre
        ),

        "Reading Status:",
        SelectBox(
            "status",
            [
                "Want to Read",
                "Currently Reading",
                "Finished"
            ],
            book.status
        ),

        "Rating:",
        SelectBox(
            "rating",
            ["0", "1", "2", "3", "4", "5"],
            str(book.rating)
        ),

        "Review:",
        TextArea("review", book.review),

        Button(
            "Save Changes",
            "save_edit",
            {"book_id": book_id}
        ),

        Button(
            "Cancel",
            "book_details",
            {"book_id": book_id}
        )
    ])

# Save Edited Book

@route
def save_edit(
    state: State,
    book_id: int,
    title: str,
    author: str,
    genre: str,
    status: str,
    rating: str,
    review: str
) -> Page:
    """Updates the info of an existing book."""
    if book_id < 0 or book_id >= len(state.books):
        state.message = "Book could not be found."
        return bookshelf(state)

    if title.strip() == "" or author.strip() == "":
        state.message = "Title and author cannot be empty."
        return edit_book(state, book_id)

    book = state.books[book_id]

    book.title = title.strip()
    book.author = author.strip()
    book.genre = genre
    book.status = status
    book.rating = int(rating)
    book.review = review.strip()

    state.message = "Your book was updated successfully!"

    return book_details(state, book_id)


# Delete Book

@route
def delete_book(state: State, book_id: int) -> Page:
    """Removes a selected book from the bookshelf."""
    if book_id < 0 or book_id >= len(state.books):
        state.message = "Book could not be found."
        return bookshelf(state)

    removed_book = state.books.pop(book_id)

    state.message = (
        removed_book.title + " was removed from your bookshelf."
    )

    state.selected_book = -1

    return bookshelf(state)

# Statistics Page

@route
def statistics(state: State) -> Page:
    """Displays the reading statistics and the yearly goal."""
    state.current_page = "Statistics"

    finished = count_finished(state.books)
    currently_reading = count_reading(state.books)
    want_to_read = count_want_to_read(state.books)

    total_ratings = 0
    rated_books = 0

    for book in state.books:
        if book.rating > 0:
            total_ratings += book.rating
            rated_books += 1

    if rated_books > 0:
        average_rating = total_ratings / rated_books
    else:
        average_rating = 0

    if state.reading_goal > 0:
        progress = finished / state.reading_goal * 100
    else:
        progress = 0

    if progress > 100:
        progress = 100

    content = [
        Header("Reading Statistics"),
        *navigation(state),

        Header("Your Reading Summary"),
        "Total Books: " + str(len(state.books)),
        "Finished Books: " + str(finished),
        "Currently Reading: " + str(currently_reading),
        "Want to Read: " + str(want_to_read),

        "Average Rating: " + str(round(average_rating, 2)),
        "Yearly Goal: " + str(state.reading_goal),
        "Goal Progress: " + str(round(progress, 1)) + "%",

        HorizontalRule(),
        Header("Update Your Reading Goal"),
        "Enter your new yearly reading goal:",
        TextBox("new_goal", state.reading_goal),
        Button("Update Goal", "update_goal"),

        HorizontalRule(),
        Header("Books by Genre")
    ]

    genres = [
        "Fantasy",
        "Romance",
        "Mystery",
        "Science Fiction",
        "Nonfiction",
        "Horror",
        "Other"
    ]

    for genre in genres:
        genre_count = 0

        for book in state.books:
            if book.genre == genre:
                genre_count += 1

        content.append(genre + ": " + str(genre_count))

    return Page(state, content)

# Update Reading Goal

@route
def update_goal(state: State, new_goal: int) -> Page:
    """Changes the user's yearly reading goal."""
    if new_goal < 1:
        state.message = "Your reading goal must be at least 1."
        return statistics(state)

    state.reading_goal = new_goal
    state.message = "Your reading goal was updated!"

    return statistics(state)

### Unit Tests

# Sample books used for testing
test_books = [
    Book("Dune", "Frank Herbert", "Science Fiction",
         "Finished", 5, "Excellent book."),
    Book("The Hobbit", "J.R.R. Tolkien", "Fantasy",
         "Currently Reading", 4, "A great adventure."),
    Book("Pride and Prejudice", "Jane Austen", "Romance",
         "Want to Read", 0, "")
]


# count_finished
assert_equal(count_finished(test_books), 1)
assert_equal(count_finished([]), 0)

# count_reading
assert_equal(count_reading(test_books), 1)
assert_equal(count_reading([]), 0)

# count_want_to_read
assert_equal(count_want_to_read(test_books), 1)
assert_equal(count_want_to_read([]), 0)

# find_duplicate
assert_equal(find_duplicate(test_books, "Dune", "Frank Herbert"), True)
assert_equal(find_duplicate(test_books, "dune", "frank herbert"), True)
assert_equal(find_duplicate(test_books, "Dune", "J.R.R. Tolkien"), False)
assert_equal(find_duplicate(test_books, "New Book", "New Author"), False)

# navigation
assert_equal(navigation(State(test_books, 5, "Home",
                              "All Books", -1, "")),
             [
                 Button("Home", "index"),
                 Button("My Bookshelf", "bookshelf"),
                 Button("Add a Book", "add_book"),
                 Button("Statistics", "statistics"),
                 HorizontalRule()
             ])


# index
home_state = State(test_books, 5, "Bookshelf",
                   "All Books", -1, "")

home_page = index(home_state)

assert_state(home_page, State(test_books, 5, "Home",
                              "All Books", -1, ""))
assert_has(home_page, "Total books: 3")
assert_has(home_page, "Books finished: 1")
assert_has(home_page, "Currently reading: 1")
assert_has(home_page, "Keep reading!")


# bookshelf
shelf_state = State(test_books, 5, "Home",
                    "All Books", -1, "")

shelf_page = bookshelf(shelf_state)

assert_state(shelf_page, State(test_books, 5, "Bookshelf",
                               "All Books", -1, ""))
assert_has(shelf_page, "Dune")
assert_has(shelf_page, "The Hobbit")
assert_has(shelf_page, "Pride and Prejudice")


# change_filter
filter_state = State(test_books, 5, "Home",
                     "All Books", -1, "")

filter_page = change_filter(filter_state, "Finished")

assert_state(filter_page, State(test_books, 5, "Bookshelf",
                                "Finished", -1, "Showing: Finished"))
assert_has(filter_page, "Dune")


# add_book
add_state = State(test_books, 5, "Home",
                  "All Books", -1, "")

add_page = add_book(add_state)

assert_state(add_page, State(test_books, 5, "Add Book",
                             "All Books", -1, ""))
assert_has(add_page, "Book Title:")
assert_has(add_page, "Author:")
assert_has(add_page, "Save Book")


# save_book
save_state = State(test_books.copy(), 5, "Add Book",
                   "Finished", -1, "")

save_page = save_book(save_state, "  1984  ", "  George Orwell  ",
                      "Other", "Finished", "5", "Great book.")

assert_state(save_page, State(
    test_books + [
        Book("1984", "George Orwell", "Other",
             "Finished", 5, "Great book.")
    ],
    5, "Bookshelf", "All Books", -1,
    "Your book was added successfully!"
))
assert_has(save_page, "1984")


# book_details
details_state = State(test_books, 5, "Bookshelf",
                      "All Books", -1, "")

details_page = book_details(details_state, 0)

assert_state(details_page, State(test_books, 5, "Book Details",
                                 "All Books", 0, ""))
assert_has(details_page, "Dune")
assert_has(details_page, "Frank Herbert")
assert_has(details_page, "Excellent book.")


# edit_book
edit_state = State(test_books, 5, "Book Details",
                   "All Books", -1, "")

edit_page = edit_book(edit_state, 1)

assert_state(edit_page, State(test_books, 5, "Edit Book",
                              "All Books", 1, ""))
assert_has(edit_page, "The Hobbit")
assert_has(edit_page, "J.R.R. Tolkien")
assert_has(edit_page, "Save Changes")


# save_edit
edit_save_state = State(test_books.copy(), 5, "Edit Book",
                        "All Books", 1, "")

edit_save_page = save_edit(
    edit_save_state, 1, "The Hobbit Updated",
    "J.R.R. Tolkien", "Fantasy", "Finished",
    "5", "Even better on a reread."
)

assert_state(edit_save_page, State(
    [
        test_books[0],
        Book("The Hobbit Updated", "J.R.R. Tolkien",
             "Fantasy", "Finished", 5,
             "Even better on a reread."),
        test_books[2]
    ],
    5, "Book Details", "All Books", 1,
    "Your book was updated successfully!"
))
assert_has(edit_save_page, "The Hobbit Updated")


# delete_book

delete_books = [
    Book("Dune", "Frank Herbert", "Science Fiction",
         "Finished", 5, "Excellent book."),
    Book("The Hobbit", "J.R.R. Tolkien", "Fantasy",
         "Currently Reading", 4, "A great adventure."),
    Book("Pride and Prejudice", "Jane Austen", "Romance",
         "Want to Read", 0, "")
]

delete_state = State(delete_books, 5, "Bookshelf",
                     "All Books", 1, "")

expected_delete_books = [
    delete_books[0],
    delete_books[2]
]

delete_page = delete_book(delete_state, 1)

assert_state(delete_page, State(
    expected_delete_books,
    5, "Bookshelf", "All Books", -1,
    "The Hobbit was removed from your bookshelf."
))

assert_has(delete_page, "Dune")
assert_has(delete_page, "Pride and Prejudice")


# statistics

stats_books = [
    Book("Dune", "Frank Herbert", "Science Fiction",
         "Finished", 5, "Excellent book."),
    Book("The Hobbit", "J.R.R. Tolkien", "Fantasy",
         "Currently Reading", 4, "A great adventure."),
    Book("Pride and Prejudice", "Jane Austen", "Romance",
         "Want to Read", 0, "")
]

stats_state = State(stats_books, 5, "Home",
                    "All Books", -1, "")

stats_page = statistics(stats_state)

assert_state(stats_page, State(stats_books, 5, "Statistics",
                               "All Books", -1, ""))

assert_has(stats_page, "Total Books: 3")
assert_has(stats_page, "Finished Books: 1")
assert_has(stats_page, "Currently Reading: 1")
assert_has(stats_page, "Want to Read: 1")
assert_has(stats_page, "Average Rating: 4.5")
assert_has(stats_page, "Goal Progress: 20.0%")

### Website Info

hide_debug_information()
set_website_title("Archive of Your Own")
set_website_framed(False)
set_site_information(author="Rhoslyn Orr", description="A digital reading log.", sources = ["Goodreads.com"],
                     planning=["CS1 Final Project 0 - Pick a Problem.pdf", "CS1 Final Project 1 - Design.pdf"],
                     links=["https://rhoslyn17.github.io/archive-of-your-own/"], server=None)

### Start Website

start_server(
    State(
        books=[ ],
        reading_goal=1,
        current_page="Home",
        active_filter="All Books",
        selected_book=-1,
        message=""
    )
)
