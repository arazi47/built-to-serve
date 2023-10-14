<h1 align="center">Webserver to go</h1>

<!--
[![Github Actions CI](https://img.shields.io/github/actions/workflow/status/arazi47/built-to-serve/.github%2Fworkflows%2Fci.yml)](https://github.com/arazi47/built-to-serve/actions/workflows/ci.yml)
![Supported Python versions](https://img.shields.io/badge/python-3.11-pink)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)
[![GitHub issues open](https://img.shields.io/github/issues/arazi47/built-to-serve)](https://github.com/arazi47/built-to-serve/issues)
-->

<p align="center">
  <a href="https://img.shields.io/github/actions/workflow/status/arazi47/built-to-serve/.github%2Fworkflows%2Fci.yml"><img src="https://img.shields.io/github/actions/workflow/status/arazi47/built-to-serve/.github%2Fworkflows%2Fci.yml"></a>
  <a href="https://img.shields.io/badge/python-3.11-pink"><img src="https://img.shields.io/badge/python-3.11-pink"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-blue"></a>
  <a href="https://github.com/arazi47/built-to-serve/issues"><img src="https://img.shields.io/github/issues/arazi47/built-to-serve"></a>
</p>

# Insallation
WS2G can be installed via `pip`. The project is avalbale on [pypi](https://pypi.org/project/ws2g/).

```console
pip install ws2g
```

# Get started
First, take a look at the example app, found [here](https://github.com/arazi47/built-to-serve-testing-app).

# Features
### Easily display your pages
This library supports all displaying images, videos, HTML/CSS and JavaScript files. The example website is built using Bootstrap.

> [!IMPORTANT]  
> All HTML/CSS/JS and other media files must be stored in `content/` (path relative to your app's `main.py`).

### Code templates
```html
<table id="gbentries-table" border = "1">
<tr>
  <th>ID</th>
  <th>Username</th>
  <th>Comment</th>
  <th>Posted on</th>
</tr>
{{customcontent}}
  {{for gbentry in gbrepo}}
    <tr>
    <td>{{gbentry.id}}</td>
    <td>{{gbentry.username}}</td>
    <td>{{gbentry.comment}}</td>
    <td>{{gbentry.posted_on}}</td>
    </tr>
  {{endfor}}
{{endcustomcontent}}
</table>
```

Notice the `{{customcontent}}` and `{{endcustomcontent}}` tags. They represent the beginning and the end of the area of code that contains custom content. Inside, there is a loop which iterates over a list of objects and displays some of its attributes on diffeernt table rows.

The resulting HTML content is this:
* TODO add code

And the result on the user's screen is this:
* TODO add pic

### No boilerplate for repositories!
```python
from built_to_serve_arazi47.repository import Repository

class UserRepository(Repository):
    pass
```

This is all you need to have a fully functioning repository (except the DTO, of course) The following methods are already implemented: `save`, `update`, `fetch_all`, `delete_by_id`. The data is stored using an SQL database.

> [!IMPORTANT]
> All repositories have to follow the convention `ModelRepository`, i.e for a class named `User`, its corresponding repository *must* be `UserRepository`.

### Easily create routes
Routes can be easily created using `@route("/identifier", "method)`, where the identifier must be prepended by `/` and method can be either `GET` or `POST`.

```python
@route("/", "GET")
@route("/bubblegum", "GET")
@route("/index", "GET")
def index():
    return render("index.html")
```

There can be multiple identifiers that call the same function, as in the above example.

### Rendering files and templates

`render("relative_path.html")` can be called to display to the browser a file stored in the `/content` directory.

### Redirecting

```python
@route("/takemehome", "GET")
def post_guest_home():
    return redirect("/")
```

`redirect("/identifier")` can be called to force the client to generate a new GET request for an identifier. The above example will generate a GET request for `/`, which will in turn call the `index()` function mentioned in the previous example.

### Path variables

```python
@route("/users/<user_id>", "GET")
def view_user(user_id):
    return "viewing user " + str(user_id)
```

Notice the above example. A GET request on `/users/123` would display `viewing user 123` in the browser.

> [!NOTE]
> In Python, all path variables are passed as strings. The user can convert them to other data types as needed.

> [!IMPORTANT]
> Valid variable names are the same as in other programming languages. (they can only contain letters, numbers and the underscore character, must not start with a letter and cannot contain any spaces.)

> [!IMPORTANT]
> Variable values can can only contain letters, numbers and the underscore character.

### Passing inputs from HTML files

Consider the following example:

```HTML
<form method="post">
	<div>
		<input id="id-input" type="text" name="id" placeholder="ID" readonly>
		<br>
		<input id="username-input" type="text" name="username" placeholder="Username">
		<br>
		<input id="comment-input" type="text" name="comment" placeholder="Comment">
		<br>
		<input id="posted-on-input" type="text" name="posted_on" placeholder="Posted on">
		<br>
		<button type="submit" name="submit_update">Save</button>
		<button type="submit" name="submit_delete">Delete</button>
	</div>
</form>
```

After clicking either the `Save` or `Delete` button, the server will receive a POST request from the path the client was on. Here's how to access the HTML inputs in Python:

```python
@route("/updateentry", "POST")
def update_entry(id, username, comment, __extra_fields):
    gbrepo = GuestBookRepository()
    if "submit_update" in __extra_fields:
        gbrepo.save(GuestBook(int(id), username, comment, datetime.now().strftime("%B %d, %Y %I:%M%p")))
    elif "submit_delete" in __extra_fields:
        gbrepo.delete(id)
    else:
        print("Unknown POST request.")

    return redirect("/adminhome")
```

Notice how `id`, `username` and `comment` are used in `update_entry`. `posted_on` can be introduced as an argument as well, but it is not needed this time. It can be found in `__extra_fields`, a variable name reserved by WS2G for such cases.

> [!IMPORTANT]
> `__extra_variables` is a reserved keyword which contains variables contained in POST requests that have not been explicitly specified as arguments to the view function. It is a dictionary, having as keys a variable name and as value the value of the input from the HTML code.

A typical use case for `__extra_variables` is to query which button was pressed in the HTML example at the beginning of the section. Explicitly naming `submit_update` or `submit_delete` will not work, because only one of the variables will be present at any one time, never both at the same time. To check which button was pressed, simply check if either variable is found in `__extra_fields`. The two variables will have an empty string as a value. Simply checking whether the key with the variable name exists is sufficient for the user to know which button was pressed.

> [!NOTE]
> In Python, input variables and the values of the keys in `__extra_fields` are passed as strings. The user can convert them to other data types as needed.

> [!IMPORTANT]
> Valid input names are the same as valid variable names in programming. (they can only contain letters, numbers and the underscore character, must not start with a letter and cannot contain any spaces.)