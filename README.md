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


# Get started
First, take a look at the example app, found [here](https://github.com/arazi47/built-to-serve-testing-app).

# Features
### Easily display your pages
This library supports all displaying images, videos, HTML/CSS and JavaScript files. The example website is built using Bootstrap.

> [!IMPORTANT]  
> All HTML/CSS/JS and other media files shouild be stored in `content/`.

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

Notice the `{{customcontent}}` and `{{endcustomcontent}}` tags? They represent the beginning, respectively the end of the area of code that contains custom content. Inside, there is a loop which iterates over a list of objects and displays some of its attributes on the screen.

The resulting HTML content is this:
* TODO add code

And the result on the user's screen is this:
* TODO add pic

### No boilerplate for repositories!
```python
from built_to_serve_arazi47.repository import Repository

class GuestBookRepository(Repository):
    pass
```

This is all you need to have a fully functioning repository (except the DTO, of course) The following methods are already implemented: `save`, `update`, `fetch_all`, `delete_by_id`. The data is stored using an SQL database.

> [!IMPORTANT]
> Be aware that you need to create a `Model` and have its repository named `ModelRepository`, i.e for a class named `User`, its corresponding repository *must* be `UserRepository`.

### Easily create routes
Routes can be easily created using `@route("path/to/file")`.

```python
@route("/")
@route("/index.html")
class Index(BaseView):
    def __init__(self, file_path, status_code=200, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()
```

The get response is as basic as it gets: it opens and displays the page located at `file_path`.
