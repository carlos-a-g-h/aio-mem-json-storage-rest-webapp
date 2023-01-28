#!/usr/bin/python3.9

# Regular imports
import asyncio

# Grabs the data
from thedata import _the_storage

# Sample function for your jobs
async def job():
	print("Job Example:\nPrint current data each 10 sec.")
	while True:
		await asyncio.sleep(10)
		print("\nData:",_the_storage)
