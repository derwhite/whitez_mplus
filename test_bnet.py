import configparser
import time
from functools import wraps
from bnet import BnetBroker


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def parse_config_file(config_file_path):
    config = configparser.ConfigParser()
    config.read(config_file_path)

    client_id = config['BNET'].get('client_id', "")
    client_secret = config['BNET'].get('client_secret', "")

    settings = {
        'client_id': client_id,
        'client_secret': client_secret
    }

    return settings


@timeit
def test_create_broker(settings):
    return BnetBroker(settings['client_id'], settings['client_secret'])


@timeit
def test_pull_realm_index(bnet_broker, iterations):
    realm_index_endpoint = f'/data/wow/realm/index'
    for i in range(iterations):
        r = bnet_broker.pull(realm_index_endpoint, namespace='dynamic-eu')


def test(settings):
    bnet_broker = test_create_broker(settings)

    test_pull_realm_index(bnet_broker, 1)
    test_pull_realm_index(bnet_broker, 10)
    test_pull_realm_index(bnet_broker, 50)


if __name__ == "__main__":
    config_file_path = "../settings.conf"
    test(parse_config_file(config_file_path))
