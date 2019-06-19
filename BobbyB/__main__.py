import os
import json
import aiohttp
from random import randint
from aiohttp import web
from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()


def get_random_quote():
	quotes = json.loads(open('quotes.json').read())
	ind = randint(0, len(quotes))
	return quotes[ind]

@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
	"""
	Whenever an issue is opened, greet the author and say thanks.
	"""
	url = event.data["issue"]["comments_url"]
	body = event.data["issue"]["body"]

	if "bobby b" in body.lower():
		message = get_random_quote()
		await gh.post(url, data={"body": message})


@router.register("issue_comment", action="created")
async def issue_comment_event(event, gh, *args, **kwargs):
	"""
	Whenever an issue is commented upon, greet the author and say thanks.
	"""
	url = event.data["issue"]["comments_url"]
	body = event.data["comment"]["body"]

	if "bobby b" in body.lower():
		message = get_random_quote()
		await gh.post(url, data={"body": message})

async def main(request):
	body = await request.read()

	secret = os.environ.get("GH_SECRET")
	oauth_token = os.environ.get("GH_AUTH")

	event = sansio.Event.from_http(request.headers, body, secret=secret)
	async with aiohttp.ClientSession() as session:
		gh = gh_aiohttp.GitHubAPI(session, "mariatta",
								  oauth_token=oauth_token)
		await router.dispatch(event, gh)
	return web.Response(status=200)


if __name__ == "__main__":
	app = web.Application()
	app.router.add_post("/", main)
	port = os.environ.get("PORT")
	if port is not None:
		port = int(port)

	web.run_app(app, port=port)
