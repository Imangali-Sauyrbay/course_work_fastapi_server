def add_oas_auth(oas: dict):
    oas['components']['securitySchemes'] = {
        'bearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
    }

    oas['security'] = [
        {
            'bearerAuth': [
                '*',
            ]
        }
    ]

    return oas