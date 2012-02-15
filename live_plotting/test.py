from data_feed import DummyDataGenerator
from publisher import NumpyPublisher
from data_source import DataSource

count = 0


def debug_callback(buffer):
    global count
    #print 'count: %s shape: %s' % (count, buffer.shape)
    count += 1

# Create reactive data generator
reactive_data_generator = DummyDataGenerator(1 / 1500.0)

# Create a data publisher
numpy_publisher = NumpyPublisher(reactive_data_generator, time_period=1/30.0)

# Start accepting data from the reactive data generator
numpy_publisher.bind()

# Create a data source
data_source = DataSource(publisher=numpy_publisher, buffer_size=10000)

# Hooks up data source to start accepting data from the publisher
data_source.bind()

# Subscribe to data from the data_source, normally plots would be doing this
data_source.subscribe(debug_callback)

