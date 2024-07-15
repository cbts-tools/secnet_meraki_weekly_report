import readline
from dotenv import load_dotenv
import os, re
from datetime import datetime
from O365 import Account, FileSystemTokenBackend
import urllib3
from pprint import pprint
from pandas import pandas
import asyncio
import meraki.aio
from webexteamssdk import WebexTeamsAPI
import reverse_geocode
# from vco_lib.vco_v1 import Vco_v1
from geopy.geocoders import Nominatim

urllib3.disable_warnings()
load_dotenv()
MERAKI_DASHBOARD_API_KEY = os.getenv("MERAKI_DASHBOARD_API_KEY")
VCO124TOKEN = os.getenv('VCO124TOKEN')
VCO160TOKEN = os.getenv('VCO160TOKEN')
VCO33TOKEN = os.getenv('VCO33TOKEN')

WEBEX_API_TOKEN = os.getenv('webex_secure_cloudnetworking_bot_token')

# ## O365 - defined in external .env ##
# app_id = os.getenv("O365app_id")
# secret = os.getenv("O365secret")
# tenant_id = os.getenv("O365tenant_id")

# geolocator = Nominatim(user_agent="spesdfasdfjasldjflkajse")

# ## List of emails to notify via Webex and O365 Email ##
# sender_address = "cloudnetautomation@cbts.com"

# mail_to_list = [
# "moshfequr.rahman@cbts.com", "nick.abbas@cbts.com"
# ]

# message_to_list = ["moshfequr.rahman@cbts.com"]

# async def get_velo_df():
#     vco = Vco_v1('vco124', VCO124TOKEN)
#     vco = Vco_v1('vco160', VCO160TOKEN)
#     vco = Vco_v1('vco33', VCO33TOKEN)

#     enterprises_count = 0
#     edges_count = 0
#     country_list_final = []
#     data_list = []
#     # ('vco33', VCO33TOKEN), ('vco160', VCO160TOKEN), ('vco124', VCO124TOKEN)
#     for v in [('vco33', VCO33TOKEN), ('vco160', VCO160TOKEN), ('vco124', VCO124TOKEN)]:
#         vco = Vco_v1(v[0], v[1])
#         enterprises = vco.getEnterprises()
#         print("Working on {} with {} enterprises....".format(v[0].upper(), len(enterprises)))
#         enterprises_count += len(enterprises)
#         country_list = []
#         coord_list = []
#         for enterprise in enterprises:
#             new_coord_list = []
#             edges = vco.getEdgesByEnterprise(enterprise['id'], detailed=False)
#             edges_count += len(edges)
#             for edge in edges:
#                 address = "{}, {}, {}, {}".format(edge['site']['streetAddress'], edge['site']['city'], edge['site']['state'], edge['site']['country'])
#                 d = {}
#                 d['vco'] = v[0]
#                 d['enterprise'] = enterprise['name']
#                 d['edge'] = edge['name']
#                 d['edgeState'] = edge['edgeState']

#                 description = edge['description']
#                 crm = re.findall(r"(\d{7,11})", str(description))
#                 if crm == []:
#                     d['crm'] = 'missing'
#                 else:
#                     d['crm'] = crm[0]

#                 d['serial_number'] = edge['serialNumber']
#                 d['ha_state'] = edge['haState']
#                 d['ha_serial_number'] = edge['haSerialNumber']
#                 d['ha_mode'] = edge['haMode']
#                 d['address'] = address
#                 d['latittude'] = edge['site']['lat']
#                 d['longitude'] = edge['site']['lon']
                
                
#                 data_list.append(d)
    

#     df = pandas.DataFrame(data_list)
#     return df



async def get_meraki_org_devices(aiomeraki: meraki.aio.AsyncDashboardAPI, org:dict):
    try:
        devices = await aiomeraki.organizations.getOrganizationDevices(org['id'], total_pages='all')
        networks = await aiomeraki.organizations.getOrganizationNetworks(org['id'], total_pages='all')
    except meraki.exceptions.AsyncAPIError as e:
        return "Error: {}".format(org['name'])
    return (org['name'], devices, networks)



def send_webex_message(text):
    # email = "moshfequr.rahman@cbts.com"
    email = "amarnath.neelameham@cbts.com"
    try:
        api = WebexTeamsAPI(access_token=WEBEX_API_TOKEN)
        # text = "Claire's Weekly Velo QoE Report - sent!"
        message = api.messages.create(toPersonEmail=email, text=text)
        print("New message created, with ID:", message.id)
        # print(message.text)
    except Exception as e:
        print("Webex Error: {}".format(e))



async def main():
    async with meraki.aio.AsyncDashboardAPI(
        MERAKI_DASHBOARD_API_KEY,
        base_url="https://api.meraki.com/api/v1",
        #log_file_prefix=__file__[:-3],
        maximum_concurrent_requests=10,
        maximum_retries=4,
        print_console=False,
        suppress_logging=True,
    ) as aiomeraki:
        total_number_of_devices = 0
        organizations = await aiomeraki.organizations.getOrganizations()
        print("Working on Meraki {} organizations.....".format(len(organizations)))
        tasks = [get_meraki_org_devices(aiomeraki, org) for org in organizations]

        data_list = []
        for task in asyncio.as_completed(tasks):
            t = await task
            if t[1] != [] and 'Error' not in t:
                total_number_of_devices += len(t[1])
                devices = t[1]
                networks = t[2]
                for device in devices:
                    coord = (device['lat'], device['lng'],)

                    
                    d = {}
                    d['organization'] = t[0]
                    d['network'], tags = next((network['name'], network['tags']) for network in networks if network['id'] == device['networkId'])
                    d['device_name'] = device['name']
                    d['serial_number'] = device['serial']
                    d['address'] = device['address']
                    d['latitude'] = device['lat']
                    d['longitude'] = device['lng']

                    data_list.append(d)
    

        df_meraki = pandas.DataFrame(data_list)
        # df_velo = await get_velo_df()


        message = "Result: {} organizations has {} devices.".format(len(organizations), len(data_list))

        print(message)

        send_webex_message(message)

        print("End")

        # with pandas.ExcelWriter("CBTS_NaaS_SDWAN_countries_all.xlsx") as writer:
        #     df_meraki.to_excel(writer, sheet_name="NaaS", index=False)
        #     df_velo.to_excel(writer, sheet_name="SDWAN", index=False)

        

        # print("Script complete!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())