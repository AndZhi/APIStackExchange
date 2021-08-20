from app.search import views


def setup_routes(app):
    app.router.add_get("/", views.all_query)
    app.router.add_get("/search", views.search)
    app.router.add_post("/response", views.response)
