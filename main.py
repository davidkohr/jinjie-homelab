import aiohttp
import asyncio
from asusrouter import AsusRouter, AsusData
from prometheus_client import Gauge, start_http_server

# Define Prometheus metrics
rx_metric = Gauge('router_network_rx_bytes', 'Received bytes', ['interface'])
tx_metric = Gauge('router_network_tx_bytes', 'Transmitted bytes', ['interface'])
rx_speed_metric = Gauge('router_network_rx_speed', 'Receive speed in bytes/sec', ['interface'])
tx_speed_metric = Gauge('router_network_tx_speed', 'Transmit speed in bytes/sec', ['interface'])

async def update_metrics(router):
    """Fetch data from the router and update Prometheus metrics."""
    network_data = await router.async_get_data(AsusData.NETWORK)

    for interface, metrics in network_data.items():
        rx_metric.labels(interface=interface).set(metrics['rx'])
        tx_metric.labels(interface=interface).set(metrics['tx'])
        rx_speed_metric.labels(interface=interface).set(metrics['rx_speed'])
        tx_speed_metric.labels(interface=interface).set(metrics['tx_speed'])

async def main():
    """Main function to initialize router and update metrics periodically."""
    # Create aiohttp session
    async with aiohttp.ClientSession() as session:
        # Initialize ASUS Router connection
        router = AsusRouter(
            hostname="router.asus.com",
            username="",
            password="",
            use_ssl=True,
            session=session,
        )

        # Start Prometheus metrics HTTP server
        start_http_server(8000)

        try:
            # Connect to the router
            await router.async_connect()
            
            # Periodically fetch and update metrics
            while True:
                await update_metrics(router)
                await asyncio.sleep(15)  # Wait for 15 seconds before the next update
        finally:
            # Disconnect and close the session when you're done
            await router.async_disconnect()
            await session.close()

# Run the asyncio event loop
if __name__ == "__main__":
    asyncio.run(main())
