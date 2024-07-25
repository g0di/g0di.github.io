---
layout: post
title: Testing Python code integration with an Azure Eventhub
tags: python azure pytest testing asyncio docker
---

On one of my project I needed to create a simple API allowing clients to publish some messages into an Azure EventHub. Because authentication is ensured by a JWT we could not rely on our clients to directly publish messages to the Eventhub (and by the way I prefer abstracting this away through a HTTP API).

> **TL;DR**
>
> To create automated tests for your service and ensure it properly publish messages to your eventhub with expected content you can use `asyncio.ensure_future()` function. It allows to run an event consumer in the background right before sending your test message. Next to that, you can leverage `asyncio.Queue` to collect received messages and compare them with what you sent at the end of your test. In the meanwhile you can use a Docker container to emulate an Azure Eventhub [Go to the solution](#wrapping-up-as-pytest-tests)

## A simple notification service

The first implementation was pretty straighforward.

> Note that I'll skip the HTTP API part as its not relevant for this article

```python
from typing import Any, Protocol

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from pydantic import TypeAdapter


class Notifier(Protocol):
    async def send(self, data: dict[str, Any]) -> None: ...


class AzureEventHubNotifier(Notifier):
    """Implementation of the Notifier port which uses an Azure Event Hub for sending notifications as events."""

    def __init__(self, eventhub_producer: EventHubProducerClient) -> None:
        self.hub = eventhub_producer
        self.type_adapter = TypeAdapter(dict[str, Any])

    async def send(self, data: dict[str, Any]) -> None:
        evt = EventData(self.type_adapter.dump_json(data))
        await self.hub.send_event(evt)
```

> Note the use of Pydantic here solely for serializing `dict` into a JSON string. In particular for types which are not converted by default by the standard `json` module like `date`.

Basically, we get a simple service with one function `send` for sending some data as a message in the event hub. The service expect an Azure `EventHubProducerClient` which is a client coming from the Azure SDK for Python in the [`azure-eventhub`](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub) package.

So far so good.

Then, I wanted to test this service. My first issue was that the eventhub I wanted to test against on Azure was actually private so I was not able to reach it directly from my machine.

## Azure Eventhub emulator

To be able to test and automate my tests against a running and available Eventhub I found out that [Microsoft actually provide a Docker container for this purpose](https://learn.microsoft.com/en-us/azure/event-hubs/test-locally-with-event-hub-emulator?tabs=docker-linux-container).

You can very quickly spin up a local Eventhub emulator for your developments using the following `docker-compose.yml` and `azure-eventhubs-emulator-config.json` files:

```yaml
# docker-compose.yml
name: healthblocks-validator-fap
services:
  eventhubs:
    image: mcr.microsoft.com/azure-messaging/eventhubs-emulator:latest
    volumes:
      - ./azure-eventhubs-emulator-config.json:/Eventhubs_Emulator/ConfigFiles/Config.json
    ports:
      - 5672:5672
    environment:
      BLOB_SERVER: azurite
      METADATA_SERVER: azurite
      ACCEPT_EULA: Y
    depends_on:
      - azurite
  azurite:
    image: mcr.microsoft.com/azure-storage/azurite:latest
    ports:
      - 10000:10000
      - 10001:10001
      - 10002:10002
```

> Note that this docker compose yaml file is coming from the Microsoft official documentation that I've simplified a bit (usage of docker network is not mandatory))

```json
// azure-eventhubs-emulator-config.json
{
  "UserConfig": {
    "NamespaceConfig": [
      {
        "Type": "EventHub",
        "Name": "emulatorNs1",
        "Entities": [
          {
            "Name": "eh1",
            "PartitionCount": "2",
            "ConsumerGroups": [
              {
                "Name": "cg1"
              }
            ]
          }
        ]
      }
    ],
    "LoggingConfig": {
      "Type": "File"
    }
  }
}
```

> This file is actually for configuring the eventhub namespace, consumer groups, entities, ...

From that point a simple `docker compose up` got you a running event hub locally after a couple of seconds. To connect to it you can simply use the connection string provided in the logs of the event hub.

```python
import asyncio

from azure.eventhub.aio import EventHubProducerClient


con_string = "Endpoint=sb://localhost:5672;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"


async def test_send_message() -> None:
    async with EventHubProducerClient.from_connection_string(
        con_string, eventhub_name="eh1"
    ) as hub:
        notifier = AzureEventHubNotifier(hub)
        await notifier.send({"Hello": "World!"})
        print("Message sent!")  # noqa: T201


asyncio.run(test_send_message())
```

> Don't forget to specify the `eventhub_name` which is not provided in the connection string directly. This value correspond to the name of an entity in your event hub json config file.

So now we have an event hub and snippet of code for testing our beautiful service. This is great but, how do we actually ensure our service properly sent the mesage to the hub? Also, what if we want to automatize this test using `pytest` for example? The best way could be to consume messages sent to the hub and ensure we actually received the one we sent so far.

> Obviously, for the sake of this example, our service is so simple that there is no doubt that if the `send` function does not raise an error, there is lot of chances that the message actually landed into the hub.

## Asyncio and Future to the rescue

To consume messages from our eventhub using the Azure SDK for Python we have to do something like this

```python
import asyncio

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient

con_string = "Endpoint=sb://localhost:5672;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"


async def on_event(_: object, event: EventData | None) -> None:
    if event is None:
        return
    print(f"Received: {event.body_as_json()}")


async def consume_messages() -> None:
    async with EventHubConsumerClient.from_connection_string(
        con_string, consumer_group="cg1"
    ) as consumer:
        await consumer.receive(on_event)


asyncio.run(consume_messages())
```

There is two main issues here:

1. The `receive` function is actually blocking. But because its a coroutine you have to put some `await` in front of it to actually dispatch it. Any code after this statement will never be executed (except if the consumer is closed for some reasons)
1. The received events are processed in a callback function so you can not put any `assert` statements here because `pytest` will not be able to catch it.

### Consuming events in the background

The first thing we have to do is to receive events in the background so we can keep running some code once started. I found out how to do this on stackoverflow (apologizes to the author, I lost the original thread) using some gem from `asyncio`

```python
import asyncio
from contextlib import suppress

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient

con_string = "Endpoint=sb://localhost:5672;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"


async def on_event(_: object, event: EventData | None) -> None:
    if event is None:
        return
    print(f"Received: {event.body_as_json()}")


async def consume_and_stop() -> None:
    # Init our consumer and producers
    async with (
        EventHubConsumerClient.from_connection_string(
            con_string, eventhub_name="eh1", consumer_group="cg1"
        ) as consumer,
        EventHubProducerClient.from_connection_string(
            con_string, eventhub_name="eh1", consumer_group="cg1"
        ) as producer,
    ):
        # Start receiving messages on the background
        task = asyncio.ensure_future(consumer.receive(on_event))
        # Wait enough time for the consumer to be settle (otherwise we may miss some events)
        await asyncio.sleep(2)

        # Send some JSON formatted events
        await producer.send_event(EventData('"Hello World!"'))
        await producer.send_event(EventData('"Foo Bar!"'))

        # Leave enough time for our consumer to receive events
        await asyncio.sleep(2)

        # Stops receiving events
        task.cancel()
        with suppress(asyncio.CancelledError):
            # Don't forget to await the task in the end to avoid your Python program to hang forever
            await task


asyncio.run(consume_and_stop())
```

```bash
Received: Hello World!
Received: Foo Bar!
```

The idea is to use `asyncio.ensure_future` function to actually dispatch our coroutine and get a `Future` object wrapping the task. This way we are no longer blocked.

We add a small sleep statement because receiving events is not instant so we could miss messages sent right after.

At the end, we cancel the task, which stops receiving events and we finally await the canceled task without raising the cancelation error.

### Accessing received events in the main thread

As we mentionned, events received are passed to a given callback function. This mechanism makes it harded to use those events in our main thread (for comparing what we sent to what we a received in a test for example).

Thanksfully there is a dedicated data structure for this use case right in the standard library: `asyncio.Queue`. We can leverage this async queue for collecting the events we received. Let's update our previous script.

```python
import asyncio
from contextlib import suppress

from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient

con_string = "Endpoint=sb://localhost:5672;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"

# Use a queue for storing events received from the callback into the main thread
events: asyncio.Queue[EventData] = asyncio.Queue()


async def on_event(_: object, event: EventData | None) -> None:
    if event is None:
        return
    # Push events in the queue
    await events.put(event)


async def consume_and_stop() -> None:
    async with (
        EventHubConsumerClient.from_connection_string(
            con_string, eventhub_name="eh1", consumer_group="cg1"
        ) as consumer,
        EventHubProducerClient.from_connection_string(
            con_string, eventhub_name="eh1", consumer_group="cg1"
        ) as producer,
    ):

        task = asyncio.ensure_future(consumer.receive(on_event))
        await asyncio.sleep(2)

        await producer.send_event(EventData('"Hello World!"'))
        await producer.send_event(EventData('"Foo Bar!"'))

        await asyncio.sleep(2)

        # Stops receiving events
        task.cancel()
        with suppress(asyncio.CancelledError):
            # Don't forget to await the task in the end to avoid your Python program to hang forever
            await task


asyncio.run(consume_and_stop())

# Collect events bodies received as strings
# NOTE: queue are not iterable so we can not simply list(events)
events_bodies = [events.get_nowait().body_as_str() for _ in range(events.qsize())]

# NOTE: The order of the events might change each run
assert '"Hello World!"' in events_bodies
assert '"Foo Bar!"' in events_bodies
```

> Note that we could also have used `pytest-docker` or `testcontainers` libraries to easily spin up our docker containers on the fly during our tests. Maybe I'll add this later on and update this article

TADA!
Now we can both produce and consume events on a same thread and then we can access received events for doing any kind of tests or verifications.

### Wrapping up as `pytest` tests

Now that we got our main pieces we can wrap it up into nice automated tests using `pytest`

```python
import asyncio
from collections.abc import AsyncIterator, Iterator
from contextlib import suppress
from typing import Any

import pytest
import pytest_asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient

from validator_fap.adapters.notifier import AzureEventHubNotifier

con_string = "Endpoint=sb://localhost:5672;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"


@pytest_asyncio.fixture
async def eventhub_producer() -> AsyncIterator[EventHubProducerClient]:
    async with EventHubProducerClient.from_connection_string(
        con_string, eventhub_name="eh1"
    ) as producer:
        yield producer


@pytest_asyncio.fixture
async def eventhub_consumer() -> AsyncIterator[EventHubConsumerClient]:
    async with EventHubConsumerClient.from_connection_string(
        con_string,
        eventhub_name="eh1",
        consumer_group="cg1",
    ) as consumer:
        yield consumer


@pytest_asyncio.fixture
async def events(
    eventhub_consumer: EventHubConsumerClient,
) -> AsyncIterator[Iterator[dict[str, Any]]]:
    """Start listening for event hubs events and returns a generator which yield received events."""
    events: asyncio.Queue[EventData] = asyncio.Queue()

    async def on_event(_: object, event: EventData | None) -> None:
        """Push events into our queue."""
        if event is not None:
            await events.put(event)

    def collect_events() -> Iterator[dict[str, Any]]:
        """Collect events in the queue as a generator.

        Using a generator here defer events loading during tests.
        """
        while not events.empty():
            yield events.get_nowait().body_as_json()

    # Start receiving messages on the background
    task = asyncio.ensure_future(eventhub_consumer.receive(on_event))
    # Wait enough time for the consumer to be settle (otherwise we may miss some events)
    await asyncio.sleep(2)
    yield collect_events()

    # Properly cancel receiver
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


@pytest.fixture
def sut(eventhub_producer: EventHubProducerClient) -> AzureEventHubNotifier:
    return AzureEventHubNotifier(eventhub_producer)


@pytest.mark.asyncio
async def test_send_health_data_publish_a_message_on_azure_event_hub(
    sut: AzureEventHubNotifier,
    events: Iterator[dict[str, Any]],
) -> None:
    # Given
    data = {"foo": "bar"}
    # When
    await sut.send(data)
    # Then
    await asyncio.sleep(1)  # slight delay before actually receiving messages
    assert list(events) == [data]
```

> Note that this code snippet omitted the `AzureEventHubNotifier` class described at the beginning of the article

Lot of stuff out there but basically:

1. We create a fixture for setting up an eventhub producer to be used be our SUT (system under test, `AzureEventHubNotifier`) to send messages to the hub.
2. We create a fixture for setting up an eventhub consumer to actually receive messages sent (if any)
3. We create another `events` fixture which takes advantage of the fact that code inside functions using `yield` statements (generators and async generators) are not executed until the generator is being consumed. Here, the `events` fixture immediately start receiving events in the background and push them into a queue. The fixture yield the result of the `collect_events()` function which itself returns a generator.
4. Our test use the `events` fixture which starts receiving events in the background and gives us a generator that will yield received events
5. After setting up our test data, we send an event, wait a couple of second for the event to be received and finally consume our events generator to compare with what we sent
