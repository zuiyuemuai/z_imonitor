
monitors = {
    'Mysql': ['SystemMonitor', 'MasterStatusMonitor'],
    'Oracle': ['SystemMonitor'],
    'Redis':['SystemMonitor'],
    'Mongodb': ['SystemMonitor']
}
rabbitmq = {
    'exchange' : 'exchange',
    'monitorRouteKey' : 'key',
    'responseRouteKey' : 'Response',
    'heartbeatRouteKey' : 'Heartbeat',
    'listenQueue' : 'local-queue',
}

