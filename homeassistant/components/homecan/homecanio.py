"""HomeCAN I/O"""

# https://developers.home-assistant.io/docs/api_lib_auth/

import asyncio
import aiohttp
from aiohttp import ClientSession, ClientResponse
import time
import json


class HomeCANio:
    def __init__(self, host: str = None, username: str = None, password: str = None) -> None:
        self._host: str
        self._username: str
        self._access_token: str
        # self._session: ClientSession = aiohttp.ClientSession()


    class Auth:
        """Class to make authenticated requests."""

        def __init__(self, websession: ClientSession, host: str, username: str, access_token: str) -> None:
            """Initialize the auth."""
            self.websession = websession
            self.host = host
            self.access_token = access_token

        async def async_request(self, method: str, path: str, **kwargs) -> ClientResponse:
            """Make a request."""
            headers = kwargs.get("headers")

            if headers is None:
                headers = {}
            else:
                headers = dict(headers)

            headers["Cookie"] = self.access_token

            return await self.websession.request(
                method, f"{self.host}/{path}", **kwargs, headers=headers, ssl=False,
            )
        
    async def async_getjson(self, lasttime: str) -> dict[str, any]:
        print(lasttime)
        async with aiohttp.ClientSession() as session:
            auth = self.Auth(session, 'https://192.168.2.6:9980', '', 'AuthToken=RaBa19640120')
            if lasttime != '' :
                lasttime = '=' + lasttime
            # This will fetch data
            resp = await auth.async_request('GET', 'Data?*.*' + lasttime)
            # print("HTTP response status code", resp.status)
            if resp.status == 200 :
                return(await resp.json())
            return(None)

    async def async_test(self, lasttime:str) -> dict[str, any]:
        datastr = '''{"Time":"2023-11-04T09:03:18.693142Z",
            "Msgs":{
            "RS_DG_Sensor":{
            "Temperature":19.229416,"Time":"2023-11-04T09:02:30.943505Z",
            "Humidity":49.898529,"Time":"2023-11-04T09:02:45.940785Z",
            "DewPoint":8.517136,"Time":"2023-11-04T09:03:00.940523Z",
            "Light":310.546875,"Time":"2023-11-04T09:03:15.940682Z"},
            "RS_Kind_V_Sensor":{
            "Temperature":19.942398,"Time":"2023-11-04T09:02:35.286355Z",
            "Humidity":49.304951,"Time":"2023-11-04T09:02:50.283288Z",
            "DewPoint":8.994299,"Time":"2023-11-04T09:03:05.283435Z",
            "Light":31.250000,"Time":"2023-11-04T09:02:20.285589Z"},
            "RS_Galerie_Sensor":{
            "Temperature":20.340000,"Time":"2023-11-04T09:02:57.083118Z",
            "Humidity":48.474751,"Time":"2023-11-04T09:03:02.082732Z",
            "DewPoint":9.121569,"Time":"2023-11-04T09:03:07.082343Z",
            "Light":167.968750,"Time":"2023-11-04T09:03:12.082416Z"},
            "RS_Kind_H_Sensor":{
            "Temperature":21.259998,"Time":"2023-11-04T09:02:56.818571Z",
            "Humidity":48.045673,"Time":"2023-11-04T09:03:01.817554Z",
            "DewPoint":9.830486,"Time":"2023-11-04T09:03:06.817725Z",
            "Light":240.234375,"Time":"2023-11-04T09:03:11.817460Z"},
            "RS_Schlafen_Sensor":{
            "Temperature":20.321587,"Time":"2023-11-04T09:01:41.481936Z",
            "Humidity":48.902115,"Time":"2023-11-04T09:02:56.476593Z",
            "DewPoint":9.220028,"Time":"2023-11-04T09:03:11.476303Z",
            "Light":832.031250,"Time":"2023-11-04T09:02:26.478949Z"},
            "RS_Bad_Sensor":{
            "Temperature":20.389999,"Time":"2023-11-04T09:02:49.722125Z",
            "Humidity":73.143555,"Time":"2023-11-04T09:02:54.721363Z",
            "DewPoint":15.420018,"Time":"2023-11-04T09:02:59.720895Z",
            "Light":160.156250,"Time":"2023-11-04T09:03:04.721162Z"},
            "RS_Kueche_Sensor":{
            "Temperature":21.090000,"Time":"2023-11-04T09:02:58.662552Z",
            "Humidity":48.889675,"Time":"2023-11-04T09:03:03.662204Z",
            "DewPoint":9.934656,"Time":"2023-11-04T09:03:08.662012Z",
            "Light":91.796875,"Time":"2023-11-04T09:03:13.661522Z"},
            "RS_Eingang_Sensor":{
            "Temperature":20.299999,"Time":"2023-11-04T09:02:25.006225Z",
            "Humidity":49.235233,"Time":"2023-11-04T09:03:00.004187Z",
            "DewPoint":9.315789,"Time":"2023-11-04T09:03:05.003991Z",
            "Light":41.015625,"Time":"2023-11-04T09:03:10.006117Z"},
            "RS_Garage_Sensor":{
            "Temperature":11.199997,"Time":"2023-11-04T09:02:48.746693Z",
            "Humidity":74.621353,"Time":"2023-11-04T09:02:53.745893Z",
            "DewPoint":6.865649,"Time":"2023-11-04T09:02:58.745717Z",
            "Light":0.000049,"Time":"2023-11-04T09:03:03.746057Z"},
            "RS_WZ_Sensor":{
            "Temperature":21.719997,"Time":"2023-11-04T09:03:18.357582Z",
            "Humidity":48.269085,"Time":"2023-11-04T09:02:53.358176Z",
            "DewPoint":10.356633,"Time":"2023-11-04T09:02:58.357715Z",
            "Light":462.890625,"Time":"2023-11-04T09:03:03.357550Z"},
            "RS_EZ_Sensor":{
            "Temperature":20.775543,"Time":"2023-11-04T09:02:25.931090Z",
            "Humidity":46.497292,"Time":"2023-11-04T09:02:40.928054Z",
            "DewPoint":8.886579,"Time":"2023-11-04T09:02:55.927547Z",
            "Light":607.421875,"Time":"2023-11-04T09:03:10.927481Z"},
            "RS_Technik2_Sensor":{
            "Temperature":21.136032,"Time":"2023-11-04T09:01:20.159820Z",
            "Humidity":45.659573,"Time":"2023-11-04T09:02:35.154039Z",
            "DewPoint":8.944943,"Time":"2023-11-04T09:02:50.153553Z",
            "Light":0.000000,"Time":"2023-11-04T09:03:05.153783Z"},
            "RS_UG_Sensor":{
            "Temperature":21.371025,"Time":"2023-11-04T09:03:06.645618Z",
            "Humidity":46.956589,"Time":"2023-11-04T09:02:21.651495Z",
            "DewPoint":9.613720,"Time":"2023-11-04T09:02:36.649517Z",
            "Light":0.000000,"Time":"2023-11-04T09:01:51.656353Z"},
            "RS_Technik1_Sensor":{
            "Temperature":22.270927,"Time":"2023-11-04T09:02:44.380192Z",
            "Humidity":43.855953,"Time":"2023-11-04T09:02:59.377271Z",
            "DewPoint":9.374481,"Time":"2023-11-04T09:03:14.377455Z",
            "Light":0.000000,"Time":"2023-11-04T08:52:29.398400Z"}
            }}'''

        data = json.loads(datastr)
        return(data)



# async def async_getmsgs(self):
#     while(True):
#         print('============================================================')
#         r = await self.async_getjson(self._lasttime)
#         if r is not None:
#             self._lasttime = r['Time']
#             m = r['Msgs']
#             print(m)
#         time.sleep(5)


# hc = HomeCANio()
# asyncio.run(hc.async_getmsgs())
