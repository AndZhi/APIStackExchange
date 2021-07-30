from app.search import views


# настраиваем пути, которые будут вести к нашей странице
def setup_routes(app):
    app.router.add_get("/", views.all_query)
    app.router.add_get("/search", views.search)
    app.router.add_get("/response", views.response)
