def kong_user_header(user_id):
    return {"x-authenticated-userid": str(user_id), "App-ID": "test"}
