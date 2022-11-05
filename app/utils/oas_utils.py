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
                'get_products',
                'get_product',
                'create_product',
                'update_product',
                'delete_product',
            ]
        }
    ]

    return oas