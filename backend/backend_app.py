from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_by = request.args.get('sort')
    direction = request.args.get('direction')

    # Validate the sort field
    if sort_by and sort_by not in ['title', 'content']:
        return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400

    # Validate the sort direction
    if direction and direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid sort direction. Use 'asc' or 'desc'."}), 400

    # Sort the posts if sort parameters are provided
    if sort_by:
        POSTS.sort(key=lambda post: post[sort_by].lower(), reverse=(direction == 'desc'))

    return jsonify(POSTS), 200


@app.route('/api/posts', methods=['POST'])
def add_posts():
    new_post = request.get_json()  # Get JSON data sent from the client
    """
    Checks if 'title' and 'content' are missing from the request.
    Missing fields are appended to the missing_fields list, and if any are found,
    an error will be returned. 
    """
    missing_fields = []
    if 'title' not in new_post:
        missing_fields.append('title')
    if 'content' not in new_post:
        missing_fields.append('content')
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    new_post['id'] = max(post['id'] for post in POSTS) + 1  # Assign a new ID
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_posts(id):
    global POSTS

    # Checks if post['id'] exist or not
    post_exists = False
    for post in POSTS:
        if post['id'] == id:
            post_exists = True
            break
    if not post_exists:
        return jsonify({"error": f"Post with id {id} is not found."}), 404

    new_post = []
    for post in POSTS:
        if post['id'] != id:
            new_post.append(post)
    POSTS = new_post
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    global POSTS

    data = request.get_json()

    post_to_update = None
    for post in POSTS:
        if post['id'] == id:
            post_to_update = post
            break

    if post_to_update is None:
        return jsonify({"error": f"Post with id {id} not found."}), 404

    # Update the post fields if they are provided in the request
    if 'title' in data:
        post_to_update['title'] = data['title']
    if 'content' in data:
        post_to_update['content'] = data['content']

    response = {
        "id": post_to_update['id'],
        "title": post_to_update['title'],
        "content": post_to_update['content']
    }

    return jsonify(response), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    matching_posts = []

    for post in POSTS:
        title_match = True
        content_match = True

        if title_query:
            title_match = title_query in post['title'].lower()

        if content_query:
            content_match = content_query in post['content'].lower()

        if title_match and content_match:
            matching_posts.append(post)

    return jsonify(matching_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
