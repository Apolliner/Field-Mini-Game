from API.base import RBase
from API.player import RPlayer, RPlayerPost


def register_routes(api):
    api.add_resource(RBase, '/base')

    api.add_resource(RPlayerPost, '/player_post')
    api.add_resource(RPlayer, '/player/<player_id>')
