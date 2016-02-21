from flask import render_template, abort, redirect, url_for

from uchan import app, g
from uchan.lib import roles
from uchan.lib.moderator_request import get_authed, get_authed_moderator


@app.route('/<board_name>/view/<int:thread_id>')
def view_thread(board_name, thread_id):
    if thread_id <= 0 or thread_id > 2 ** 32:
        abort(400)

    board_config_cached = g.board_cache.find_board_config_cached(board_name)
    if not board_config_cached:
        abort(400)

    thread_cached = g.posts_cache.find_thread_cached(thread_id)

    if thread_cached and thread_cached.board.name == board_name:
        show_moderator_buttons = get_authed() and g.moderator_service.has_role(get_authed_moderator(), roles.ROLE_ADMIN)

        return render_template('thread.html', thread=thread_cached, board_config=board_config_cached.board_config, show_moderator_buttons=show_moderator_buttons)
    else:
        abort(404)


@app.route('/find_post/<int:post_id>')
def find_post(post_id):
    if post_id <= 0 or post_id > 2 ** 32:
        abort(400)

    post = g.posts_service.find_post(post_id)
    if post:
        return redirect(url_for('view_thread', board_name=post.thread.board.name, thread_id=post.thread.id) + '#p' + str(post.refno))
    else:
        abort(404)