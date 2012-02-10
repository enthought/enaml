from feeds import DummyDataGenerator, NumpyFeed
from subscription import NumpySubscription
from datasource import DataSource

native_feed = DummyDataGenerator(1 / 100000.0)
numpy_feed = NumpyFeed(native_feed)
data_source = DataSource()
subscription = NumpySubscription(data_source, numpy_feed, time_period=3, pass_through=False,
                                sample_probability=0.5)
subscription.start()
