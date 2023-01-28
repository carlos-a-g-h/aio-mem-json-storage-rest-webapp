#!/usr/bin/python3.9

# AIO mem-cached JSON storage REST-ful web server

import asyncio
import json
import os
import logging

from aiohttp import web

from thedata import _the_storage
from thedata import _html_homepage
from myjobs import job

#do_jobs=False
#try:
#	from myjobs import job
#except:
#	logging.error("No jobs found")
#else:
#	do_jobs=True

################################################################################

_logfile="log.txt"
open(_logfile,"wt")
logging.basicConfig(filename=_logfile,format='[%(levelname) 5s/%(asctime)s] %(name)s: %(msg)s',level=logging.ERROR)
logging.error("Initializing JSONStore...")

################################################################################

# ENV VARS

# PASSWORD: (Text) Password for creating, updating or deleting data
# PRIVATE: (Bool) Wether a password is needed or not to retrieve data from the storage with a GET request
# PORT: (Number) Port used by the webserver
# SEQUENTIAL: (Bool)

_ev_password=os.getenv("PASSWORD","12345678")
_ev_port=os.getenv("PORT","80")

def eval_bool(invalue):
	if not invalue==None:
		invalue=invalue.strip()
		invalue=invalue.lower()

	if invalue in ["false","true"]:
		vd={"false":False,"true":True}
		value=vd[invalue]
	else:
		value=False

	return value

_ev_private=eval_bool(os.getenv("PRIVATE","True"))

del eval_bool

################################################################################

# Filters

async def filter_main(request):

	targets=[]
	wutt=False
	status_code=200
	req_data={}

	try:
		req_data_raw=await request.text()
		req_data_raw=req_data_raw.strip()
		print(req_data_raw)
	except Exception as e:
		wutt=True
		status_code=400
		print("filter_main(0)",status_code,e)

	if not wutt:
		try:
			to_json=json.loads(req_data_raw)
		except:
			to_json=None
		else:
			req_data=to_json

		if not to_json:
			try:
				assert req_data_raw.startswith("{") and req_data_raw.endswith("}")
				to_json=eval(req_data_raw)
			except Exception as e:
				wutt=True
				status_code=400
				print("filter_main(1)",status_code,e)

			else:
				req_data=to_json

	if not wutt:
		if not (req_data.get("password")==_ev_password):
			wutt=True
			status_code=401
			print("filter_main(2)",status_code,"password mismach")

	return (req_data,wutt,status_code)

def filter_keys_and_op(req_data):

	operation=None

	key_value_pair=(("key" in req_data) and ("value" in req_data))
	key_value_pair_list=("kvpairs" in req_data)
	key_one=("key" in req_data)
	key_list=("keys" in req_data)

	con_w_one=(key_value_pair and (not key_value_pair_list) and (not key_list))
	con_w_multi=(key_value_pair_list and (not key_value_pair) and (not key_one) and (not key_list))
	con_r_one=False
	con_r_multi=False

	if con_w_one:
		operation="w"

	if con_w_multi:
		operation="w"

	if (not key_value_pair) and (not key_value_pair_list):
		if key_one and (not key_list):
			operation="r"
			con_r_one=True

		if (not key_one) and key_list:
			operation="r"
			con_r_multi=True

	return (con_w_one,con_w_multi,con_r_one,con_r_multi,operation)

################################################################################

# Other

def read_from_store(req_data,con_r_one,con_r_multi):

	the_list=[]

	if con_r_one:
		the_key=req_data["key"]
		the_list.append(the_key)

	if con_r_multi:
		key_list=req_data["keys"]
		if type(key_list)==list:
			for key in key_list:
				the_list.append(key)

	return the_list

################################################################################

async def handler_get(request):

	# GET /

	# Get value from existing keys (only if not private)
	# → Get a value from a specific key: "/?key=keyname"
	# → Get the whole storage (a bit dangerous and unnecessary): "/"

	response={}
	status_code=200

	if _ev_private:
		return web.Response(body=_html_homepage,content_type="text/html",charset="utf-8",status=200)

	if not _ev_private:
		get_key=request.query.get("key")

		if get_key:
			the_value=_the_storage.get(get_key)
			if the_value:
				response=the_value

			if not the_value:
				status_code=404
				print("GET / 2",status_code)

		if not get_key:
			response=_the_storage.copy()

	return web.Response(body=json.dumps(response),content_type="application/json",charset="utf-8",status=status_code)

async def handler_post(request):

	# POST /

	# Create or update a key+value pair:
	#{"password":"password","key":"keyname","value":{"any":"thing","you":[want],"in":[4,"json"]}}

	# Create or update multiple key+value pairs:
	# {"password":"password","kvpairs":{"key1":"val1","key2":"val2","key3":"val3","keyN":"valN"}}

	# Get a value from an existing key (only if private):
	# {"password":"password","key":"keyname"}
	# Returns key+value like this {"keyname":"value"} if found, otherwise, it returns nothing

	# Get multiple values from multiple keys (only if private):
	# {"password":"password":"keys":["key1","key2","keyN"]}
	# Returns all keys and values found like this {"key1":"value1","key2":"value2","keyN":"valueN"}

	response={}
	operation=None

	req_data,wutt,status_code=await filter_main(request)

	if not wutt:
		con_w_one,con_w_multi,con_r_one,con_r_multi,operation=filter_keys_and_op(req_data)

		if not operation:
			wutt=True
			status_code=406
			print("POST / 1:",status_code)

	if operation=="w":
		# create or update

		the_list=[]

		if con_w_one:
			pair={req_data["key"]:req_data["value"]}
			the_list.append(pair)

		if con_w_multi:
			all_pairs=req_data["kvpairs"]
			if type(all_pairs) is dict:
				for pair in all_pairs:
					the_list.append({pair:all_pairs[pair]})

		if len(the_list)==0:
			wutt=True
			status_code=406
			print("POST / 2:",status_code)

		if not wutt:
			for pair in the_list:
				_the_storage.update(pair)
				response.update(pair)

	if operation=="r":
		# read only

		the_list=read_from_store(req_data,con_r_one,con_r_multi)

		if len(the_list)==0:
			wutt=True
			status_code=406
			print("POST / 3:",status_code)

		if not wutt:
			processed=0
			for key in the_list:
				if key in _the_storage:
					processed=processed+1
					response.update({key:_the_storage.get(key)})

			if processed==0:
				wutt=True
				status_code=406
				print("POST / 4:",status_code)

	print("POST / END:",_the_storage)
	return web.Response(body=json.dumps(response),content_type="application/json",charset="utf-8",status=status_code)

async def handler_delete(request):

	# DELETE /

	# It always returns an empty JSON, so keep an eye for the status code

	# Delete a key and it's value:
	# {"password":"password","key":"keyname"}

	# Delete multiple keys along with their corresponding values:
	# {"password":"password","keys":["key1","key2","key3","keyN"]}

	response={}
	operation=None

	req_data,wutt,status_code=await filter_main(request)

	if not wutt:
		con_w_one,con_w_multi,con_r_one,con_r_multi,operation=filter_keys_and_op(req_data)

		if not operation=="R":
			wutt=True
			status_code=406
			print("DELETE / 1:",status_code)

	if not wutt:

		the_list=read_from_store(req_data,con_r_one,con_r_multi)

		if len(the_list)==0:
			wutt=True
			status_code=406
			print("DELETE / 2:",status_code)

		if not wutt:

			processed=0
			for key in the_list:
				if key in _the_storage:
					processed=processed+1
					del _the_storage[key]

			if processed==0:
				wutt=True
				status_code=406
				print("DELETE / 3:",status_code)

	print("DELETE / END:",_the_storage)
	return web.Response(body=json.dumps(response),content_type="application/json",charset="utf-8",status=status_code)

################################################################################

# Running the server

async def build_app():
	app=web.Application()
	app.add_routes([
		web.get("/",handler_get),
		web.post("/",handler_post),
		web.delete("/",handler_delete)
	])
	return app

if "job" in dir():
	this_loop=asyncio.get_event_loop()

	print("current loop status:")

	print(this_loop)

	#if do_jobs:
	#	print("running task...")
	#	this_loop.create_task(job())

	print("running task...")

	this_loop.create_task(job())

print("current loop status:")

print(this_loop)

print("running webserver...")
web.run_app(build_app(),port=_ev_port)

################################################################################

# Any resemblace to Redis or any other key-value-pair-non-SQL DB is purely coincidential because this project is obviously not a DB...
