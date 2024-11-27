from aws_lambda_powertools import Logger


def get_logger():
    level = "DEBUG"
    logger = Logger(
        service="search_embeddings_app", level=level, location="%(module)s.%(funcName)s:%(lineno)d"
    )
    return logger