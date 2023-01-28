#!/usr/bin/python3.9

_the_storage={}

_html_homepage="""
<!DOCTYPE html>
<html lang="en">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<head>
<title>
JSONStore UI
</title>
<script>
	async function request(del)
	{
		let thepassword=document.getElementById("thepassword").value;
		let keyname=document.getElementById("keyname").value;
		let value=document.getElementById("value").value;

		thepassword=thepassword.trim();
		keyname=keyname.trim();
		value=value.trim();

		json_text="{";
		json_text=json_text+"\\"password\\":\\""+thepassword+"\\",";

		if (keyname.length>0)
		{
			json_text=json_text+"\\"keyname\\":\\""+keyname+"\\",";
		};

		if (del===false && (keyname.length>0) && (value.length>0))
		{
			json_text=json_text+"\\"value\\":\\""+value+"\\",";
		};

		json_text=json_text+"}";

		let the_method="post";
		if (del===true)
		{
			the_method="delete";
		};

		console.log(the_method+" "+json_text);

		let response=await fetch("/",
		{
			method:the_method,
			headers:{"Accept":"*/*","Content-Type":"application/json"},
			body:json_text
		});

		let message=""
		if (response.ok)
		{
			message=await response.text();
		}
		else
		{
			message="???";
		};

		document.getElementById("output").innerHTML=message;
	};

	function clear_output()
	{
		document.getElementById("output").innerHTML="";
	};
</script>
<body>
	<div id="input">
		<p>Password<br><br><input id="thepassword" type="text"></input></p>
		<p>Key<br><br><input id="keyname" type="text"></input></p>
		<p>Value<br><br><input id="value" type="text"></input></p>
		<p>Actions<br><br><button onclick="request(false);">Get or Set</button><br><br><button onclick="request(true);">Delete</button><br><br><button onclick="clear_output();">Clear output</button></p>
	</div>
	<div id="output">
	</div>
</body>
</html>
"""
