# gt-django

### Introduction

This guide will walk you through setting up a Django project named `core` and creating a simple application, `gt`, which will render a table using the `GT` library.

### Steps

1. **Create a New Django Project**

   Start by creating a new Django project called `core`:

   ```bash
   django-admin startproject core .
   ```

2. **Create a New Django App**

   Next, create a new Django app named `gt`:

   ```bash
   python manage.py startapp gt
   ```

3. **Add the `gt` App to `INSTALLED_APPS`**

   Include the `gt` app in the `INSTALLED_APPS` list within the `core/settings.py` file:

   ```python
   # core/settings.py

   INSTALLED_APPS = [
       "django.contrib.admin",
       "django.contrib.auth",
       "django.contrib.contenttypes",
       "django.contrib.sessions",
       "django.contrib.messages",
       "django.contrib.staticfiles",
       "gt",
   ]
   ```

4. **Create a `urls.py` in the `gt` App**

   Create a `urls.py` file in the `gt` app to define your app’s URL patterns:

   ```python
   # gt/urls.py

   from django.urls import path
   from . import views

   urlpatterns = [
       path("", views.index, name="index"),
   ]
   ```

5. **Include `gt/urls.py` in the Project’s `urls.py`**

   Modify the `core/urls.py` file to include the `gt` app’s URLs:

   ```python
   # core/urls.py

   from django.contrib import admin
   from django.urls import include, path

   urlpatterns = [
       path("admin/", admin.site.urls),
       path("", include("gt.urls")),
   ]
   ```

6. **Create the `index` View**

   Edit the `gt/views.py` file to define the `index` view. This view will generate an HTML table using `GT.as_raw_html()`:

   ```python
    # gt/views.py

    from functools import cache

    import polars as pl
    from django.shortcuts import render
    from great_tables import GT, html
    from great_tables.data import sza


    @cache
    def get_sza():
        return pl.from_pandas(sza)


    def index(request):
        sza_pivot = (
            get_sza()
            .filter((pl.col("latitude") == "20") & (pl.col("tst") <= "1200"))
            .select(pl.col("*").exclude("latitude"))
            .drop_nulls()
            .pivot(values="sza", index="month", on="tst", sort_columns=True)
        )

        sza_gt = (
            GT(sza_pivot, rowname_col="month")
            .data_color(
                domain=[90, 0],
                palette=["rebeccapurple", "white", "orange"],
                na_color="white",
            )
            .tab_header(
                title="Solar Zenith Angles from 05:30 to 12:00",
                subtitle=html("Average monthly values at latitude of 20&deg;N."),
            )
            .sub_missing(missing_text="")
        )

        context = {"sza_gt": sza_gt.as_raw_html()}

        return render(request, "gt/index.html", context)
   ```

7. **Set Up the Template**

   Create a `templates` directory within the `gt` app. Inside `templates`, create another directory named `gt`. Then, create an `index.html` file in the `gt` directory. This file will render the HTML table generated in the `index` view. Remember to use the `safe` template tag to prevent Django from escaping the HTML:

   ```html
   <!DOCTYPE html>
   <html lang="en">
     <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <meta http-equiv="X-UA-Compatible" content="ie=edge">
       <title>Django-GT Website</title>
     </head>
     <body>
       <main>
           <h1 style="text-align:center">Great Tables shown in Django</h1>  
       </main>
       <div>
           {{ sza_gt | safe}}
       </div>
     </body>
   </html>
   ```

8. **Migrate the Database**

   Apply migrations to set up your database:

   ```bash
   python manage.py migrate
   ```

9. **Run the Development Server**

   Finally, start the development server and open your browser to view the rendered table:

   ```bash
   python manage.py runserver
   ```

### Alternative steps
If you prefer not to use the `safe` template tag method, you can adopt the `mark_safe()` approach in the view instead. Here’s a possible implementation for your reference:

   ```python
    # gt/views.py

    from functools import cache

    import polars as pl
    from django.shortcuts import render
    from django.utils.safestring import mark_safe
    from great_tables import GT, html
    from great_tables.data import sza


    def mark_gt_safe(gt):
        if isinstance(gt, GT):
            return mark_safe(gt.as_raw_html())
        return gt


    @cache
    def get_sza():
        return pl.from_pandas(sza)


    def index(request):
        sza_pivot = (
            get_sza()
            .filter((pl.col("latitude") == "20") & (pl.col("tst") <= "1200"))
            .select(pl.col("*").exclude("latitude"))
            .drop_nulls()
            .pivot(values="sza", index="month", on="tst", sort_columns=True)
        )

        sza_gt = (
            GT(sza_pivot, rowname_col="month")
            .data_color(
                domain=[90, 0],
                palette=["rebeccapurple", "white", "orange"],
                na_color="white",
            )
            .tab_header(
                title="Solar Zenith Angles from 05:30 to 12:00",
                subtitle=html("Average monthly values at latitude of 20&deg;N."),
            )
            .sub_missing(missing_text="")
        )

        context = {"sza_gt": mark_gt_safe(sza_gt)}

        return render(request, "gt/index.html", context)
   ```

By doing this, you can use `{{ sza_gt }}` instead of `{{ sza_gt | safe }}` in the template.

You should now see the table displayed in your browser at http://127.0.0.1:8000.

![image](https://github.com/user-attachments/assets/ddccc7cd-e9db-4d31-8599-dd3e4402a910)
