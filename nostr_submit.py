import asyncio
import os
import json
import hashlib
from ecdsa import SigningKey, NIST256p
import websockets


def decode_nip19(nsec):
    # Dummy implementation for decoding nip19, assuming nsec is a string
    return {'type': 'stype', 'data': nsec}


async def connect(websocket):
    await websocket.send(json.dumps({"t": "connect"}))


async def sub(websocket, pk):
    await websocket.send(json.dumps({
        "t": "sub",
        "d": [
            {
                "kinds": [1],
                "authors": [pk]
            }
        ]
    }))


async def publish(websocket, event):
    await websocket.send(json.dumps({"t": "pub", "d": event}))


async def handle_response(websocket):
    while True:
        response = await websocket.recv()
        print(response)


def get_public_key(signing_key):
    return signing_key.get_verifying_key().to_string().hex()


def get_event_hash(event):
    sha = hashlib.sha256()
    sha.update(json.dumps(event, sort_keys=True).encode('utf-8'))
    return sha.hexdigest()


def sign_event(event, sk):
    return sk.sign(event['id'].encode('utf-8')).hex()


async def publish_to_nostr(summary):
    nsec = os.environ['SK']
    decoded_nip19 = decode_nip19(nsec)

    if isinstance(decoded_nip19['data'], str):
        sk = SigningKey.from_secret_exponent(int(decoded_nip19['data']), curve=NIST256p)
        pk = get_public_key(sk)
        event = {
            "kind": 1,
            "pubkey": pk,
            "created_at": int(os.time()),
            "tags": [],
            "content": f"{summary}",
            "id": "",
            "sig": "",
        }

        event['id'] = get_event_hash(event)
        event['sig'] = sign_event(event, sk)

        async with websockets.connect("wss://relay.damus.io") as websocket:
            await connect(websocket)
            await sub(websocket, pk)
            await publish(websocket, event)

            await handle_response(websocket)


if __name__ == "__main__":
    asyncio.run(main())
