import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "meharlabs-development-key"
    )


    MYSQL_HOST = os.environ.get(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_USER = os.environ.get(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.environ.get(
        "MYSQL_PASSWORD",
        ""
    )

    MYSQL_DB = os.environ.get(
        "MYSQL_DB",
        "meharLabs"
    )

    MYSQL_PORT = int(
        os.environ.get(
            "MYSQL_PORT",
            3306
        )
    )


    UPLOAD_FOLDER = os.path.join(
        "static",
        "uploads"
    )


        
    # EMAIL CONFIGURATION
    

    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.environ.get(
            "MAIL_PORT",
            587
        )
    )

    MAIL_USE_TLS = os.environ.get(
        "MAIL_USE_TLS",
        "True"
    ).lower() == "true"

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME",
        "loveindiabyvishal9616@gmail.com"
    )

    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD",
        "prbpfrxnsovrmgbc"
    )

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "loveindiabyvishal9616@gmail.com"
    )