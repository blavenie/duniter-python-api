import asyncio
import aiohttp

import duniterpy.api.bma as bma
from duniterpy.documents import BMAEndpoint, BlockUID, SelfCertification
from duniterpy.key import SigningKey


# CONFIG #######################################

# You can either use a complete defined endpoint : [NAME_OF_THE_API] [DOMAIN] [IPv4] [IPv6] [PORT]
# or the simple definition : [NAME_OF_THE_API] [DOMAIN] [PORT]
# Here we use the BASIC_MERKLED_API
BMA_ENDPOINT = "BASIC_MERKLED_API cgeek.fr 9330"

# Credentials should be prompted or kept in a separate secure file
# create a file with the salt on the first line and the password on the second line
# the script will load them from the file
FROM_CREDENTIALS_FILE = "/home/username/.credentials.txt"

# Your unique identifier in the Web of Trust
UID = "MyIdentity"

################################################

# Latest duniter-python-api is asynchronous and you have to create an aiohttp session to send request
# ( http://pythonhosted.org/aiohttp )
AIOHTTP_SESSION = aiohttp.ClientSession()

async def get_current_block(connection):
    """
    Get the current block data

    :param bma.api.ConnectionHandler connection: Connection handler

    :rtype: dict
    """
    # Here we request for the path blockchain/block/N
    return await bma.blockchain.Current(connection).get(AIOHTTP_SESSION)


def get_identity_document(current_block, uid, salt, password):
    """
    Get an Identity document

    :param dict current_block: Current block data
    :param str uid: Unique Identifier
    :param str salt: Passphrase of the account
    :param str password: Password of the account

    :rtype: SelfCertification
    """

    # get current block BlockStamp
    timestamp = BlockUID(current_block['number'], current_block['hash'])

    # create keys from credentials
    key = SigningKey(salt, password)

    # create identity document
    identity = SelfCertification(
        version=2,
        currency=current_block['currency'],
        pubkey=key.pubkey,
        uid=uid,
        ts=timestamp,
        signature=None
    )

    # sign document
    identity.sign([key])

    return identity

async def main():
    """
    Main code
    """
    # connection handler from BMA endpoint
    connection = BMAEndpoint.from_inline(BMA_ENDPOINT).conn_handler()

    # capture current block to get version and currency and blockstamp
    current_block = await get_current_block(connection)

    # load credentials from a text file
    salt, password = open(FROM_CREDENTIALS_FILE).readlines()

    # cleanup newlines
    salt, password = salt.strip(), password.strip()

    # create our signed identity document
    identity = get_identity_document(current_block, UID, salt, password)

    # send the identity document to the node
    data = {identity: identity.signed_raw()}
    response = await bma.wot.Add(connection).post(AIOHTTP_SESSION, **data)

    print(response)

    response.close()

with AIOHTTP_SESSION:

    # Latest duniter-python-api is asynchronous and you have to use asyncio, an asyncio loop and a "as" on the data.
    # ( https://docs.python.org/3/library/asyncio.html )
    asyncio.get_event_loop().run_until_complete(main())
