system = {
    'monitors': {
        'Mysql': ['MasterStatusMonitor'],
        'Oracle': [],
        'Redis': [],
        'Mongodb': []
    },
    'rabbitmq': {
            'exchange': 'exchange',
            'monitorRouteKey': 'Monitor',
            'responseRouteKey': 'Response',
            'heartbeatRouteKey': 'HeartBeat',
            'listenQueue': 'listen-queue',
        'asyncRouteKey':'AsyncResponse',
    }
}
