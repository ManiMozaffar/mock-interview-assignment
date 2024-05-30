### The Architecture

I would have used PostgreSQL, using Array to store the vendors. There might be a dedicated database, to handle vectors, but I don't think we're gonna query the index anyway. I might be wrong tho.

I would break it into two service, one a `KB_OPS`, which process any operation regarding knowledge base, such as querying for similiar document.
And the other service would be a FastAPI, to talk to this service. Reason is that I don't want to make the FastAPI stateful, by loading a ML model on top of it. They'd probably talk with each other using a broker. I'd choose Kafka, because I think having the messages stored, being able to replay them is quite important for ML operation, and one optimization I could do with Kafka is to do batch processing with timeout, to ensure that system is as real time as we want, but also batching all queries together, making it more efficient. Configuring RabbitMQ to have durable messages, so that I can replay them would be also an alternative approach.

### Testing

Overtesting is just as bad as undertesting in my book. I don't have the technical knowledge to know how to benchmark or QA a ML model, but other than that, from backend operation it makes sense to have 2 types of test for this assignment.

- First to ensure API works as intended, from the client perspective, using Integration testing
- Second unit test, to test some low level logics that is too much effort to test using integration, and is actually testing one very specific behaviour and unit at a time.
