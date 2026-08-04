import bcrypt



def hash_password(password):

    if not password:

        raise ValueError(
            "Password cannot be empty"
        )


    password_bytes = password.encode(
        "utf-8"
    )


    salt = bcrypt.gensalt()


    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt
    )


    return hashed_password.decode(
        "utf-8"
    )



def check_password(password, hashed_password):

    if not password or not hashed_password:

        return False


    try:

        password_bytes = password.encode(
            "utf-8"
        )


        hashed_bytes = hashed_password.encode(
            "utf-8"
        )


        return bcrypt.checkpw(
            password_bytes,
            hashed_bytes
        )


    except Exception:

        return False